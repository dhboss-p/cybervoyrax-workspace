from app import create_app
from app.services.container import build_services


def test_app_factory_registers_phase3_blueprints():
    app = create_app()
    endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}

    assert "health.health" in endpoints
    assert "api_system.backend_status" in endpoints
    assert "account.account_overview" in endpoints
    assert "directory.directory_list" in endpoints
    assert "projects.project_list" in endpoints
    assert "documents.document_detail" in endpoints
    assert "admin.admin_overview" in endpoints


def test_service_container_builds():
    app = create_app()

    with app.app_context():
        services = build_services()

        assert "auth" in services
        assert "users" in services
        assert "projects" in services
        assert "documents" in services
