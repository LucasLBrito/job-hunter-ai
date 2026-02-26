$VPS_USER = "lucasdevbrito-jobhunter"
$VPS_IP = "187.77.50.247"
$REMOTE_PATH = "~/job-hunter-ai"

echo "Compactando arquivos do projeto..."
tar -czvf project.tar.gz --exclude="apps/backend/venv" --exclude="apps/backend/__pycache__" --exclude="apps/backend/data" --exclude="apps/frontend/node_modules" --exclude="apps/frontend/.next" apps docker-compose.vps.yml

echo "Criando pasta na VPS..."
ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${REMOTE_PATH}/data ${REMOTE_PATH}/logs"

echo "Enviando o arquivo compactado..."
scp project.tar.gz "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/"

echo "Descompactando na VPS..."
ssh "${VPS_USER}@${VPS_IP}" "cd ${REMOTE_PATH} && tar -xzf project.tar.gz && mv docker-compose.vps.yml docker-compose.yml"

echo "Enviando arquivos de variaveis de ambiente..."
scp ./apps/backend/.env.vps "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/apps/backend/.env"
scp ./apps/frontend/.env.vps "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/apps/frontend/.env"

echo "Limpando arquivo compactado local..."
Remove-Item project.tar.gz

echo "Arquivos enviados com sucesso!"
echo "Em seguida, vamos executar os containers na VPS!"
