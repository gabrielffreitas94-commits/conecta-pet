# 🐾 Conecta Pet — Plataforma em Python (Site Web + App Mobile + Backend Escalável)

Marketplace estilo **iFood / Uber** escrito 100% em **Python 3.10+** que conecta **Tutores (Donos de Pets)** a **Médicos Veterinários** em 3 modalidades:
1. 🏥 **No Consultório**
2. 🚗 **Visita Domiciliar**
3. 💻 **Consulta Online (Telemedicina)**

- **100% Gratuito para Tutores e Veterinários:** O pagamento da consulta é feito diretamente ao veterinário (PIX, maquininha ou dinheiro).
- **Pré-Orçamento / Solicitação Ágil:** O tutor escolhe o profissional na vitrine por preço, distância, especialidade e avaliação, envia a solicitação e combina o atendimento.
- **Compatível 100% Offline:** Utiliza a biblioteca padrão do Python 3.10+ (`http.server`, `threading`, `uuid`, `unittest`, `urllib`) e avatares/CSS locais embutidos, sem depender de CDNs externas.

---

## 📂 Estrutura do Projeto (Python)

- [PRD.md](file:///c:/Users/Pichau/Desktop/conecta_pet/PRD.md) — Documento de Requisitos do Produto e Arquitetura para Grande Escala.
- [app.py](file:///c:/Users/Pichau/Desktop/conecta_pet/app.py) — Ponto de entrada principal (`http://localhost:8000`).
- [pyproject.toml](file:///c:/Users/Pichau/Desktop/conecta_pet/pyproject.toml) & [requirements.txt](file:///c:/Users/Pichau/Desktop/conecta_pet/requirements.txt) — Configuração do pacote Python.
- [conecta_pet/server.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/server.py) — Servidor HTTP Multi-Thread Stateless servindo a REST API JSON (`/api/*`) e a interface Web/App Mobile SSR (`/`, `/actions/*`).
- [conecta_pet/services.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/services.py) — Regras de negócio, vitrine geoespacial, cadastro ágil de veterinários/pets, pré-orçamentos e avaliações.
- [conecta_pet/infra/geo.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/infra/geo.py) — Cálculo geodésico (Haversine) e indexação espacial por células (`Geo-Cell`).
- [conecta_pet/infra/cache.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/infra/cache.py) — Camada de Cache Thread-Safe com TTL e invalidação por prefixo.
- [conecta_pet/infra/queue.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/infra/queue.py) — Fila Assíncrona de Eventos (`AsyncJobQueue`) para notificações e recálculo de notas em background.
- [conecta_pet/infra/uuidv7.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/infra/uuidv7.py) — Gerador `UUIDv7` (RFC 9562) ordenado temporalmente.
- [conecta_pet/db/schema.sql](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/db/schema.sql) — Schema PostgreSQL 16 para grande escala.
- [conecta_pet/web/ui.py](file:///c:/Users/Pichau/Desktop/conecta_pet/conecta_pet/web/ui.py) — Renderizador SSR em Python do Site Web + Simulador do App Mobile.
- [tests/test_conecta_pet.py](file:///c:/Users/Pichau/Desktop/conecta_pet/tests/test_conecta_pet.py) — Suíte de testes automatizados (`unittest`).

---

## 🚀 Como Executar

```bash
# 1. Iniciar o Servidor (Site Web + Simulador App Mobile + REST API na porta 8000)
python app.py

# 2. Executar os testes automatizados
python -m unittest discover -s tests -v
```
