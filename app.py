import os
from conecta_pet.server import create_http_server


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = create_http_server(host=host, port=port)

    print("===================================================================")
    print("🐾 CONECTA PET — Plataforma em Python (Site + App + Backend API)")
    print("===================================================================")
    print(f"🌐 Site Web & Simulador App Mobile: http://localhost:{port}")
    print(f"🚀 REST API (Vitrine Vets):         http://localhost:{port}/api/vets")
    print(f"📊 Telemetria de Grande Escala:     http://localhost:{port}/api/metrics")
    print("===================================================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor Conecta Pet...")
        server.server_close()


if __name__ == "__main__":
    main()
