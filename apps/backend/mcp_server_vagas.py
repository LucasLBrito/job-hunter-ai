"""
MCP Server — Engine de Vagas Job Hunter AI
Expõe as funções de busca e análise como ferramentas para Claude Desktop.

Como usar:
1. pip install mcp openai (se ainda não instalado)
2. Configure claude_desktop_config.json (veja abaixo)
3. Execute: python mcp_server_vagas.py

Exemplo de claude_desktop_config.json:
{
  "mcpServers": {
    "job-hunter": {
      "command": "python",
      "args": ["<caminho_absoluto>/apps/backend/mcp_server_vagas.py"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "DATABASE_URL": "sqlite+aiosqlite:///./data/database.db"
      }
    }
  }
}
"""

import json
import asyncio
import sys
import os
from typing import Any

# Adiciona o diretório do backend ao path para importações funcionarem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

# ─────────────────────────────────────────────────────────────────────────────
# Inicialização do servidor MCP
# ─────────────────────────────────────────────────────────────────────────────

server = Server("job-hunter-ai")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos (sem depender do banco de dados FastAPI)
# ─────────────────────────────────────────────────────────────────────────────

async def _buscar_vagas_standalone(termo: str, limit: int = 30) -> list:
    """
    Executa uma busca rápida em todas as plataformas disponíveis sem usar o banco.
    Retorna vagas no formato dict compatível com o analisador.
    """
    import httpx
    from bs4 import BeautifulSoup
    
    resultados = []
    
    # 1. RemoteOK (JSON público, sem auth)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://remoteok.com/api",
                headers={"Accept": "application/json", "User-Agent": "JobHunterAI/1.0"}
            )
            if r.status_code == 200:
                jobs = r.json()
                for j in jobs[1:limit]:  # primeiro item é metadata
                    if not isinstance(j, dict):
                        continue
                    tags = j.get("tags", [])
                    if termo.lower() not in str(tags).lower() and termo.lower() not in str(j.get("position", "")).lower():
                        continue
                    resultados.append({
                        "titulo": j.get("position", "N/A"),
                        "empresa": j.get("company", "N/A"),
                        "localizacao": "Remoto",
                        "descricao": j.get("description", ""),
                        "url_vaga": j.get("url", ""),
                        "fonte": "RemoteOK",
                        "id_fonte": f"remoteok-{j.get('id', hash(j.get('url', '')))}",
                    })
    except Exception as e:
        print(f"[MCP] RemoteOK error: {e}", file=sys.stderr)

    # 2. Gupy API pública
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://portal.api.gupy.io/api/v1/jobs",
                params={"jobName": termo, "limit": 20},
                headers={"Accept": "application/json"},
            )
            if r.status_code == 200:
                for item in r.json().get("data", []):
                    resultados.append({
                        "titulo": item.get("name") or item.get("jobName", "N/A"),
                        "empresa": item.get("careerPageName", "Confidencial"),
                        "localizacao": item.get("city") or item.get("state") or "Brasil",
                        "descricao": item.get("description", ""),
                        "url_vaga": item.get("jobUrl", ""),
                        "fonte": "Gupy",
                        "id_fonte": f"gupy-{item.get('id', '')}",
                    })
    except Exception as e:
        print(f"[MCP] Gupy error: {e}", file=sys.stderr)

    return resultados


async def _analisar_vagas_standalone(vagas: list, max_vagas: int = 20, perfil: dict = None) -> list:
    """Analisa vagas usando o JobAIAnalyzer sem precisar do contexto FastAPI."""
    from app.services.job_ai_analyzer import JobAIAnalyzer
    analyzer = JobAIAnalyzer(perfil=perfil)
    return await analyzer.analisar_lote(vagas, max_vagas=max_vagas)


# ─────────────────────────────────────────────────────────────────────────────
# Definição das ferramentas MCP
# ─────────────────────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="buscar_vagas",
            description=(
                "Busca vagas em múltiplas plataformas (RemoteOK, Gupy, etc.) "
                "para um termo de busca. Retorna vagas padronizadas em JSON."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "termo": {
                        "type": "string",
                        "description": "Cargo ou palavra-chave (ex: 'Python Developer', 'Data Engineer')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número máximo de vagas por plataforma (padrão: 20)",
                        "default": 20
                    }
                },
                "required": ["termo"]
            }
        ),
        types.Tool(
            name="analisar_vagas_com_ia",
            description=(
                "Analisa e filtra vagas usando IA (GPT-4o-mini), pontuando 0-100 "
                "e recomendando: APLICAR, CONSIDERAR ou IGNORAR."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "vagas_json": {
                        "type": "string",
                        "description": "JSON string com lista de vagas (retorno de buscar_vagas)"
                    },
                    "max_vagas": {
                        "type": "integer",
                        "description": "Máximo de vagas para analisar (padrão: 20)",
                        "default": 20
                    },
                    "perfil_json": {
                        "type": "string",
                        "description": "JSON opcional com perfil do candidato (cargo_desejado, skills, etc.)"
                    }
                },
                "required": ["vagas_json"]
            }
        ),
        types.Tool(
            name="buscar_e_analisar",
            description=(
                "Fluxo completo: busca vagas E analisa com IA em uma única chamada. "
                "Retorna as melhores vagas ordenadas por pontuação."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "termo": {
                        "type": "string",
                        "description": "Cargo ou palavra-chave para buscar"
                    },
                    "max_vagas": {
                        "type": "integer",
                        "description": "Máximo de vagas para analisar (padrão: 15)",
                        "default": 15
                    },
                    "perfil_json": {
                        "type": "string",
                        "description": "JSON opcional com perfil do candidato"
                    }
                },
                "required": ["termo"]
            }
        ),
        types.Tool(
            name="ver_perfil_padrao",
            description="Mostra o perfil padrão usado nas análises com IA.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Execução das ferramentas
# ─────────────────────────────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:

    # ── Ver perfil padrão ────────────────────────────────────────────────────
    if name == "ver_perfil_padrao":
        from app.services.job_ai_analyzer import JobAIAnalyzer
        analyzer = JobAIAnalyzer()
        texto = f"""# Perfil Padrão do Candidato

**Cargo Desejado:** {analyzer.perfil['cargo_desejado']}
**Nível:** {analyzer.perfil['nivel']}
**Modalidade:** {analyzer.perfil['modalidade']}
**Salário Mínimo:** R$ {analyzer.perfil['salario_minimo']:,}
**Skills Principais:** {', '.join(analyzer.perfil['skills_principais']) or 'Não definido'}
**Skills Bônus:** {', '.join(analyzer.perfil['skills_bonus']) or 'Não definido'}
**Palavras Bloqueadas:** {', '.join(analyzer.perfil['nao_quero']) or 'Nenhuma'}

*Para customizar, passe `perfil_json` nas ferramentas de análise.*
"""
        return [types.TextContent(type="text", text=texto)]

    # ── Buscar vagas ─────────────────────────────────────────────────────────
    elif name == "buscar_vagas":
        termo = arguments["termo"]
        limit = arguments.get("limit", 20)
        vagas = await _buscar_vagas_standalone(termo, limit=limit)
        resultado = {"total": len(vagas), "termo_buscado": termo, "vagas": vagas}
        return [types.TextContent(
            type="text",
            text=f"Encontradas **{len(vagas)} vagas** para '{termo}'.\n\n```json\n{json.dumps(resultado, ensure_ascii=False, indent=2)}\n```"
        )]

    # ── Analisar vagas com IA ────────────────────────────────────────────────
    elif name == "analisar_vagas_com_ia":
        try:
            vagas = json.loads(arguments["vagas_json"])
            if isinstance(vagas, dict) and "vagas" in vagas:
                vagas = vagas["vagas"]
        except json.JSONDecodeError:
            return [types.TextContent(type="text", text="❌ Erro: vagas_json inválido.")]

        perfil = None
        if arguments.get("perfil_json"):
            try:
                perfil = json.loads(arguments["perfil_json"])
            except Exception:
                pass

        max_vagas = arguments.get("max_vagas", 20)
        vagas_analisadas = await _analisar_vagas_standalone(vagas, max_vagas=max_vagas, perfil=perfil)
        return [types.TextContent(type="text", text=_formatar_relatorio(vagas_analisadas))]

    # ── Buscar + Analisar ────────────────────────────────────────────────────
    elif name == "buscar_e_analisar":
        termo = arguments["termo"]
        max_vagas = arguments.get("max_vagas", 15)
        perfil = None
        if arguments.get("perfil_json"):
            try:
                perfil = json.loads(arguments["perfil_json"])
            except Exception:
                pass

        vagas = await _buscar_vagas_standalone(termo, limit=max_vagas * 2)
        vagas_analisadas = await _analisar_vagas_standalone(vagas, max_vagas=max_vagas, perfil=perfil)

        aplicar = [v for v in vagas_analisadas if v.get("analise_ia", {}).get("recomendacao") == "APLICAR"]
        considerar = [v for v in vagas_analisadas if v.get("analise_ia", {}).get("recomendacao") == "CONSIDERAR"]

        linhas = [
            f"# Busca + Análise IA: '{termo}'",
            f"**Total coletado:** {len(vagas)} | **Analisadas:** {len(vagas_analisadas)}",
            f"🟢 Aplicar: {len(aplicar)} | 🟡 Considerar: {len(considerar)}\n",
        ]
        for v in aplicar + considerar:
            a = v.get("analise_ia", {})
            emoji = "🟢" if a.get("recomendacao") == "APLICAR" else "🟡"
            linhas.append(f"{emoji} **[{a.get('pontuacao', 0)}/100] {v.get('titulo')}** @ {v.get('empresa')}")
            linhas.append(f"   📍 {v.get('localizacao')} | {v.get('fonte')}")
            linhas.append(f"   🔗 {v.get('url_vaga')}")
            linhas.append(f"   {a.get('motivo')}\n")

        return [types.TextContent(type="text", text="\n".join(linhas))]

    else:
        return [types.TextContent(type="text", text=f"❌ Ferramenta '{name}' não reconhecida.")]


def _formatar_relatorio(vagas_analisadas: list) -> str:
    aplicar = [v for v in vagas_analisadas if v.get("analise_ia", {}).get("recomendacao") == "APLICAR"]
    considerar = [v for v in vagas_analisadas if v.get("analise_ia", {}).get("recomendacao") == "CONSIDERAR"]

    linhas = [f"# Análise de {len(vagas_analisadas)} Vagas\n"]
    linhas.append(f"🟢 **APLICAR:** {len(aplicar)} | 🟡 **CONSIDERAR:** {len(considerar)}\n")

    if aplicar:
        linhas.append("## 🟢 Aplicar Agora\n")
        for v in aplicar:
            a = v.get("analise_ia", {})
            linhas.append(f"### [{a.get('pontuacao', 0)}/100] {v.get('titulo', v.get('title', ''))} @ {v.get('empresa', v.get('company', ''))}")
            linhas.append(f"- 📍 {v.get('localizacao', v.get('location', ''))} | Fonte: {v.get('fonte', v.get('source_platform', ''))}")
            linhas.append(f"- 🔗 {v.get('url_vaga', v.get('source_url', ''))}")
            linhas.append(f"- 💡 {a.get('motivo', '')}")
            linhas.append(f"- ✅ {' | '.join(a.get('pontos_positivos', []))}\n")

    if considerar:
        linhas.append("## 🟡 Considerar\n")
        for v in considerar:
            a = v.get("analise_ia", {})
            linhas.append(f"**[{a.get('pontuacao', 0)}/100]** {v.get('titulo', v.get('title', ''))} @ {v.get('empresa', v.get('company', ''))} — {a.get('motivo', '')}")
            linhas.append(f"🔗 {v.get('url_vaga', v.get('source_url', ''))}\n")

    return "\n".join(linhas)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="job-hunter-ai",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
