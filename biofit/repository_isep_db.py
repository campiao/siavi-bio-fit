import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import List
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host='vsgate-s1.dei.isep.ipp.pt',
        port=10238,
        user='group4',
        password='SIAVIgroup4',
        database='biofit'
    )


# Define o "model" como estrutura de dados
@dataclass
class Player:
    name: str
    age: int
    gender: str
    face_encoding: list
    nrLogs: int = 1
    level: int = 1
    score: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_db_tuple(self):
        return (
            self.id,
            self.name,
            self.age,
            self.gender,
            json.dumps(self.face_encoding),  # Serializa o vetor como JSON
            self.nrLogs,
            self.level,
            self.score
        )

    @staticmethod
    def from_db_row(row):
        return Player(
            id=row[0],
            name=row[1],
            age=row[2],
            gender=row[3],
            face_encoding=json.loads(row[4]),  # Desserializa o JSON
            nrLogs=row[5],
            level=row[6],
            score=row[7]
        )




def get_data() -> List[Player]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Players')
    rows = cursor.fetchall()
    conn.close()
    return [Player.from_db_row(row) for row in rows]


def register(player: Player):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Players (id, name, age, gender, face_encoding, nr_logs, level, score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', player.to_db_tuple())
    conn.commit()
    conn.close()



def extract_encodings(players: List[Player]) -> List[List[float]]:
    return [player.face_encoding for player in players]



def update_player(player: Player) -> bool:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Players
        SET name=%s, age=%s, gender=%s, face_encoding=%s, nr_logs=%s, level=%s, score=%s
        WHERE id=%s
    ''', (
        player.name,
        player.age,
        player.gender,
        json.dumps(player.face_encoding),
        player.nrLogs,
        player.level,
        player.score,
        player.id
    ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    player1 = Player(
        name="Alice",
        age=22,
        gender="F",
        face_encoding=[1,2,1.5,-0.0000001]
    )   

    player2 = Player(
        name="Bruno",
        age=28,
        gender="M",
        face_encoding=[])
    register(player2)
    print("Pessoa adicionada com sucesso.")
    print(get_data())

