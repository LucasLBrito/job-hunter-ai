"""
Job AI Analyzer — Analisa e classifica vagas com OpenAI GPT-4o-mini.
Adaptação async do ai_analyzer.py da pasta 'alteracao' para o projeto job-hunter-ai.
Integra com as preferências do usuário e usa o OpenAI client já configurado no projeto.
"""
import logging
import json
from typing import List, Dict, Any, Optional

from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class JobAIAnalyzer:
    """
    Analisa vagas de emprego com GPT-4o-mini, pontuando 0-100 e recomendando:
    APLICAR | CONSIDERAR | IGNORAR
    
    Pode ser usado standalone ou integrado ao endpoint /jobs/analyze-batch.
    """

    def __init__(self, perfil: Optional[Dict[str, Any]] = None):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("JobAIAnalyzer: OPENAI_API_KEY não configurado. Análise desativada.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        
        # Perfil padrão — pode ser sobrescrito via parâmetro (user preferences)
        self.perfil = perfil or {
            "cargo_desejado": "Desenvolvedor",
            "nivel": "Pleno",
            "modalidade": "Remoto",
            "salario_minimo": 0,
            "skills_principais": [],
            "skills_bonus": [],
            "nao_quero": [],
            "localizacao_preferida": "Qualquer",
        }

    # -------------------------------------------------------------------------
    # Filtro rápido PRÉ-IA (economiza tokens)
    # -------------------------------------------------------------------------

    def filtro_rapido(self, vaga: Dict[str, Any]) -> bool:
        """
        Descarta vagas com palavras bloqueadas antes de chamar a API.
        Economiza tokens e tempo.
        """
        palavras_bloqueadas = self.perfil.get("nao_quero", [])
        if not palavras_bloqueadas:
            return True
        texto = (
            f"{vaga.get('title', '')} {vaga.get('description', '')} {vaga.get('location', '')}"
        ).lower()
        for palavra in palavras_bloqueadas:
            if palavra.lower() in texto:
                logger.debug(f"Vaga descartada (filtro '{palavra}'): {vaga.get('title')}")
                return False
        return True

    # -------------------------------------------------------------------------
    # Análise individual com IA
    # -------------------------------------------------------------------------

    async def analisar_vaga(self, vaga: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia uma vaga para o GPT e recebe análise estruturada (JSON).
        Retorna a vaga enriquecida com 'analise_ia'.
        """
        if not self.client:
            vaga["analise_ia"] = {
                "pontuacao": 0,
                "recomendacao": "IGNORAR",
                "motivo": "Análise IA não disponível (OPENAI_API_KEY não configurado)",
                "pontos_positivos": [],
                "pontos_negativos": [],
                "salario_estimado": "Não informado",
            }
            return vaga

        prompt_sistema = """
Você é um especialista em recrutamento de TI. Analise a vaga e compare com o perfil do candidato.
Responda APENAS em JSON válido, sem texto extra, sem markdown.

Estrutura obrigatória:
{
  "pontuacao": <número 0-100>,
  "recomendacao": "<APLICAR | CONSIDERAR | IGNORAR>",
  "motivo": "<resumo em 1-2 frases>",
  "pontos_positivos": ["<item>", ...],
  "pontos_negativos": ["<item>", ...],
  "salario_estimado": "<valor ou 'Não informado'>"
}
"""
        texto_vaga = f"""
PERFIL DO CANDIDATO:
{json.dumps(self.perfil, ensure_ascii=False, indent=2)}

VAGA PARA ANALISAR:
Título: {vaga.get('title', 'N/A')}
Empresa: {vaga.get('company', 'N/A')}
Localização: {vaga.get('location', 'N/A')}
Remoto: {vaga.get('is_remote', False)}
Fonte: {vaga.get('source_platform', 'N/A')}
Descrição: {(vaga.get('description') or 'Sem descrição disponível')[:2000]}
URL: {vaga.get('source_url') or vaga.get('url', 'N/A')}
"""
        try:
            resposta = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": texto_vaga},
                ],
                temperature=0.2,
                max_tokens=500,
            )
            texto = resposta.choices[0].message.content.strip()
            analise = json.loads(texto)
            vaga["analise_ia"] = analise
        except json.JSONDecodeError as e:
            logger.warning(f"JobAIAnalyzer: JSON parse error para '{vaga.get('title')}': {e}")
            vaga["analise_ia"] = {
                "pontuacao": 0,
                "recomendacao": "ERRO",
                "motivo": "Falha ao parsear resposta da IA",
                "pontos_positivos": [],
                "pontos_negativos": [],
                "salario_estimado": "Não informado",
            }
        except Exception as e:
            logger.error(f"JobAIAnalyzer: OpenAI API error para '{vaga.get('title')}': {e}")
            vaga["analise_ia"] = {
                "pontuacao": 0,
                "recomendacao": "ERRO",
                "motivo": str(e),
                "pontos_positivos": [],
                "pontos_negativos": [],
                "salario_estimado": "Não informado",
            }
        return vaga

    # -------------------------------------------------------------------------
    # Análise em lote
    # -------------------------------------------------------------------------

    async def analisar_lote(
        self, vagas: List[Dict[str, Any]], max_vagas: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Analisa um lote de vagas com filtro prévio e limite de chamadas.
        Retorna lista ordenada por pontuação decrescente.
        """
        import asyncio

        logger.info(f"JobAIAnalyzer: iniciando análise de {len(vagas)} vagas (max={max_vagas})")

        # 1. Filtro rápido sem IA
        vagas_filtradas = [v for v in vagas if self.filtro_rapido(v)]
        logger.info(f"JobAIAnalyzer: {len(vagas_filtradas)} vagas passaram no filtro rápido")

        # 2. Limitar para controlar custos
        para_analisar = vagas_filtradas[:max_vagas]

        # 3. Análise async simultânea (com semáforo para não sobrecarregar a API)
        semaforo = asyncio.Semaphore(5)  # máx 5 chamadas simultâneas

        async def analisar_com_semaforo(vaga):
            async with semaforo:
                return await self.analisar_vaga(vaga)

        resultados = await asyncio.gather(
            *[analisar_com_semaforo(v) for v in para_analisar],
            return_exceptions=False,
        )

        # 4. Ordenar por pontuação
        resultados.sort(
            key=lambda x: x.get("analise_ia", {}).get("pontuacao", 0),
            reverse=True,
        )
        logger.info(f"JobAIAnalyzer: análise concluída para {len(resultados)} vagas")
        return resultados

    # -------------------------------------------------------------------------
    # Construir perfil a partir do User model do projeto
    # -------------------------------------------------------------------------

    @classmethod
    def from_user(cls, user) -> "JobAIAnalyzer":
        """
        Cria um JobAIAnalyzer usando as preferências do usuário do banco de dados.
        Aceita o model User do projeto (app/models/user.py).
        """
        import json as _json

        def parse_json_list(val) -> list:
            if not val:
                return []
            try:
                return _json.loads(val) if isinstance(val, str) else list(val)
            except Exception:
                return []

        job_titles = parse_json_list(getattr(user, "job_titles", None))
        techs = parse_json_list(getattr(user, "technologies", None))
        work_models = parse_json_list(getattr(user, "work_models", None))
        locations = parse_json_list(getattr(user, "preferred_locations", None))

        # Determinar modalidade preferida
        modalidade = "Qualquer"
        if work_models:
            wm_lower = [m.lower() for m in work_models]
            if any(m in wm_lower for m in ["remote", "remoto"]):
                modalidade = "Remoto"
            elif any(m in wm_lower for m in ["hybrid", "híbrido", "hibrido"]):
                modalidade = "Híbrido"

        perfil = {
            "cargo_desejado": job_titles[0] if job_titles else "Desenvolvedor",
            "nivel": getattr(user, "seniority_level", "Pleno") or "Pleno",
            "modalidade": modalidade,
            "salario_minimo": getattr(user, "salary_min", 0) or 0,
            "skills_principais": techs[:5] if techs else [],
            "skills_bonus": techs[5:10] if len(techs) > 5 else [],
            "nao_quero": [],  # o usuário pode customizar via futuro endpoint
            "localizacao_preferida": locations[0] if locations else "Qualquer",
        }
        return cls(perfil=perfil)
