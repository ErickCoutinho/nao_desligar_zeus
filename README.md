# não_desligar_zeus

Impede que o headset Redragon Zeus Pro (H510-PRO) desligue sozinho por inatividade quando conectado pelo adaptador USB sem fio.

## Como funciona

Enquanto o programa estiver aberto, ele envia ao headset um tom de 20 Hz em volume muito baixo, por 1 segundo, a cada 4min50s. O som é imperceptível, mas o headset o reconhece como áudio e não desliga. As outras saídas de som do Windows não são afetadas.

## Uso

1. Baixe o [`NaoDesligarZeus.exe`](https://github.com/ErickCoutinho/n-o_desligar_zeus/releases/latest/download/NaoDesligarZeus.exe) da [última versão](https://github.com/ErickCoutinho/n-o_desligar_zeus/releases/latest).
2. Conecte o adaptador USB do headset.
3. Abra o `NaoDesligarZeus.exe`. Ele roda sem janela, com um ícone de fone vermelho na bandeja do sistema, perto do relógio.
4. Para parar, clique com o botão direito no ícone e escolha **Sair**.

Passe o mouse sobre o ícone para ver o horário do último sinal enviado.

## Gerar o executável

Requer Windows e Python 3.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\pyinstaller --onefile --windowed --icon headphones.ico --name NaoDesligarZeus keep_alive.py
```

O executável fica em `dist\NaoDesligarZeus.exe`.

## Limitações

- Funciona apenas no Windows.
- Procura um dispositivo de saída com `H510-PRO` no nome. Para outro headset, altere `DEVICE_NAME_FRAGMENT` em `keep_alive.py`.
