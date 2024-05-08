import nox

TEST_ENV = dict(
    OPENAI_API_TYPE="test",
    OPENAI_API_VERSION="test",
    AZURE_OPENAI_ENDPOINT="test",
    AZURE_OPENAI_API_KEY="test",
    GPT4_DEPLOYMENT_NAME="test",
    GPT4_MODEL_NAME="test",
    GPT35_DEPLOYMENT_NAME="test",
    GPT35_MODEL_NAME="test",
    EMBEDDING="test",
    MONGO_DB="test",
    MONGO_CONN_STR="test",
    RAW_MESSAGE_COLLECTION="test",
    HISTORY_WINDOW_SIZE="100",
    SEARCH_ENDPOINT="test",
    SEARCH_API_KEY="test",
    SEARCH_INDEX_NAME="test",
    KB_FIELDS_SOURCEPAGE="test",
    KB_FIELDS_CONTENT="test",
    AZURE_STORAGE_ACCOUNT="test",
    AZURE_STORAGE_ACCOUNT_CRED="test",
    AZURE_STORAGE_CONTAINER="test",
    APP_NAME="test",
    AZURE_CLIENT_ID="test",
    AZURE_TENANT_ID="test",
    AZURE_CLIENT_SECRET="test",
    OPENAI_API_KEY="test",
    OPENAI_DIRECT_MODEL="test",
    SEARCH_CATALOG_NAME="test",
    KB_FIELDS_TEXT="test",
    NON_SESSION_ID="test",
    N4J_URI="test",
    N4J_USERNAME="test",
    N4J_PASSWORD="test",
    UNIVERSITY_NAME="test",
    SAML_METADATA_URL="http://test.com/metadata",
    SAML_CERT="test",
    SAML_FIRST_NAME_ATTR="test",
    SAML_LAST_NAME_ATTR="test",
    SAML_EMAIL_ATTR="test",
    BASE_URL="http://test.com:8000",
    CLIENT_BASE_URL="http://test.com:3000"
)


@nox.session(python=["3.11"])
def tests(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("coverage", "run", "-m", "pytest", "--block-network", env=TEST_ENV)
    session.run("coverage", "report", "--omit=test_*.py,mock_*.py,__init__.py")


@nox.session
def lint(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("black", "--check", ".")
    session.run("flake8", ".")


@nox.session
def typing(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("mypy", "--explicit-package-bases", ".")
