from starlette.testclient import TestClient

def test_crear_tecnico_como_admin(client: TestClient, admin_token_headers: dict[str, str]):
    """
    Prueba que un admin PUEDE crear un técnico.
    """
    response = client.post(
        "/tecnicos/",
        json={
            "codigo": "JP001",  # <-- CAMPO REQUERIDO AÑADIDO
            "nombre_completo": "Juan Perez"  # <-- NOMBRE DE CAMPO CORREGIDO
        },
        headers=admin_token_headers  # <-- Usamos el token de admin
    )

    # Verificamos que la API respondió con 201 (Creado)
    assert response.status_code == 201
    
    # Verificación extra (opcional pero recomendada)
    data = response.json()
    assert data["nombre_completo"] == "Juan Perez"
    assert data["codigo"] == "JP001"
    assert "id" in data


def test_listar_tecnicos(client: TestClient, admin_token_headers: dict[str, str]):
    """
    Prueba que se pueden listar los técnicos.
    Primero crea uno para asegurarse de que la lista no esté vacía.
    """
    # 1. Crear un técnico de prueba
    response_create = client.post(
        "/tecnicos/",
        json={
            "codigo": "AG002",  # <-- CAMPO REQUERIDO AÑADIDO
            "nombre_completo": "Ana Gomez"  # <-- NOMBRE DE CAMPO CORREGIDO
        },
        headers=admin_token_headers
    )
    # Es buena idea verificar que la creación funcionó antes de seguir
    assert response_create.status_code == 201

    # 2. Pedir la lista
    response = client.get("/tecnicos/", headers=admin_token_headers)

    # 3. Verificar
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Debe ser una lista
    assert len(data) > 0  # No debe estar vacía
    
    # Verificamos que los datos creados están en la lista
    assert any(item["nombre_completo"] == "Ana Gomez" for item in data)