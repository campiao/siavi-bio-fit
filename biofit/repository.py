import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import List

db = "biofit/database.json"

# Define o "model" como estrutura de dados
@dataclass
class Player:
    name: str
    age: int
    gender: str
    face_encoding: list
    nrLogs: int = 0
    level: int = 1
    score: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


def get_data() -> List[Player]:
    try:
        with open(db, 'r') as f:
            data = json.load(f)
            return [Player(**item) for item in data['Players']]
    except FileNotFoundError:
        return []


def register(player: Player):
    try:
        with open(db, 'r') as f:
            dados = json.load(f)  # Carrega pessoas já salvas
    except FileNotFoundError:
        dados = []  # Se o arquivo não existir, começa com lista vazia

    dados['Players'].append(asdict(player))  # Adiciona nova pessoa

    with open(db, 'w') as f:  # Salva tudo novamente
        json.dump(dados, f, indent=4)



def extract_encodings(players: List[Player]) -> List[List[float]]:
    return [player.face_encoding for player in players]



def update_player(player: Player) -> bool:
    try:
        with open(db, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"Players": []}

    found = False
    for i, item in enumerate(data["Players"]):
        if item.get("id") == player.id:
            data["Players"][i] = asdict(player)
            found = True
            break

    if not found:
        data["Players"].append(asdict(player))

    with open(db, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return True

if __name__ == "__main__":
    player1 = Player(
    name="Alice",
    age=22,
    gender="F",
    nrLogs=5,
    level=3,
    score=1200.5,
    face_encoding=[1,2,1.5,-0.0000001]
    )   

    player2 = Player(
    name="Bruno",
    age=28,
    gender="M",
    nrLogs=12,
    level=6,
    score=2450.75,
    face_encoding=[])
    register(player1)
    print("Pessoa adicionada com sucesso.")

