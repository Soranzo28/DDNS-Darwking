# 💣 Darkwing - Agente para Dungeons & Data Structures (DNDS)

Este repositório contém o **Darkwing**, um agente autônomo desenvolvido em Python para competir na arena **Dungeons & Data Structures (DNDS)**, um jogo de sobrevivência e estratégia no estilo Bomberman criado pela CoderOne.

## Estratégia e Lógica do Agente

O Darkwing é construído com base em um sistema guiado por **Objetivos com Troca de Estados**. A cada turno, o método next_move avalia o ambiente e transita entre 5 estados de ação, priorizados da seguinte forma:

1. **Fugir (fugir)**: Prioridade máxima. O agente mapeia as zonas de risco das bombas e da fumaça (método atualizar_mapa_perigo). Caso esteja em perigo, ele traça uma rota de fuga segura para longe das explosões.
2. **Coletar Tesouro (coletar_tesouro)**: Se não houver perigo imediato, o agente usa Busca em Largura (BFS) para encontrar a rota mais curta até os tesouros do mapa (tesouro_proximo).
3. **Coletar Munição (coletar_municao)**: Se identificar bombas coletáveis próximas, o agente formula um plano para pegá-las e recarregar seu inventário.
4. **Coletar Caixa (coletar_caixa)**: O agente procura caixas de madeira (sb) por perto e planta bombas estrategicamente para abrir caminho e farmar pontos.
5. **Explorar (explorar)**: Caso nenhuma das condições acima seja satisfeita, o agente entra em modo de exploração, realizando movimentos aleatórios ('u', 'd', 'l', 'r') sempre priorizando posições seguras mapeadas por vizinhanca_livre.

### Mecânicas de Pathfinding
- **Busca em Largura (BFS)**: Implementada para encontrar a rota mais curta desviando de obstáculos sólidos (sb, ib, ob) e zonas de perigo mapeadas.
- **Geometria de Táxi (Distância de Manhattan)**: Utilizada como heurística rápida pelo método distancia para avaliar alvos próximos.

## 🎮 Sobre o Ambiente (DNDS)

DNDS é uma arena onde agentes em Python competem por pontos. 
- **Início:** Cada agente inicia com 3 vidas e 3 bombas.
- **Pontuação e Itens:**
  - Tesouros (t): Permanecem no mapa até serem coletados.
  - Blocos de Madeira (sb): Quebram com 1 bomba (+1 ponto).
  - Blocos de Minério (ob): Quebram com 3 bombas (+10 pontos).
  - Oponentes: Podem ser explodidos para ganhar 25 pontos e remover uma vida.
  - Bombas de munição: Aparecem de tempo em tempo e somem após determinado intervalo 
- **Fim de jogo:** Termina quando restar apenas um agente vivo ou após 3 minutos de duração (vence quem tiver mais pontos).

## Instalação (Windows)

A instalação recomendada utiliza **Python 3.8** ou **3.10** em um ambiente virtual isolado.

1. Clone este repositório.
2. Baixe o pacote do jogo [CoderOne](https://github.com/CoderOneHQ/dungeons-and-data-structures) fornecido pela organização e coloque em uma pasta chamada dungeon.
3. Abra o Prompt de Comando do Windows e execute os comandos abaixo para criar o ambiente:

python -m venv venv
venv\Scripts\activate

4. Com o ambiente ativado, instale as dependências essenciais:

``` shell
pip install dungeon-0.1.6.tar.gz
pip install pyglet==1.5.11 pillow==8.4
```

**Atenção - Correção de Bug do Ambiente:**
Caso ocorra um erro ao iniciar o jogo relacionando ao pacote de geometria, abra o arquivo autogeometry.py (indicado na saída do terminal), vá até a linha 148 e substitua-a pela seguinte linha:


`class PolylineSet(collections.abc.Sequence):`

## Como Executar o Jogo 


Para rodar o ambiente no modo interativo (onde o player 1 pode jogar contra o Darkwing pelo teclado):

python -m coderone.dungeon.main --interactive darkwing.py

Nota: O jogo começará pausado. Pressione Enter para iniciar.

Para testes de desenvolvimento contínuos, onde o jogo recarrega o agente toda vez que você salvar o arquivo darkwing.py, utilize a flag --watch:

```python -m coderone.dungeon.main --interactive --watch darkwing.py```

Sempre que fechar o terminal e voltar ao projeto, lembre-se de ativar o ambiente virtual novamente usando: `venv\Scripts\activate`

<small>Para mais informações acesse a página do jogo no github: https://github.com/CoderOneHQ/dungeons-and-data-structures </small>

## Criando seu próprio agente

Para criar seu próprio agente criar seu arquivo agente.py, o repositório oficial do jogo dispobiliza um [agente base](https://github.com/CoderOneHQ/dungeons-and-data-structures/blob/master/random_agent.py) para a criação do seu! 
Você pode competir contra darkwing utilizando o seguinte comando:

```python -m coderone.dungeon.main seu_agente.py agente_base.py```
