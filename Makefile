.PHONY: help install sample qdrant ingest index run api ui eval test lint docker

help:
	@echo "VeriFin — common commands"
	@echo "  make install   Install Python dependencies"
	@echo "  make sample    Copy the demo document into data/raw/"
	@echo "  make qdrant    Start a local Qdrant (Docker)"
	@echo "  make ingest    Build chunks from data/raw/"
	@echo "  make index     Embed + build the vector index"
	@echo "  make run Q='..' Answer one question from the CLI"
	@echo "  make api       Run the FastAPI backend on :8000"
	@echo "  make ui        Run the Streamlit frontend"
	@echo "  make eval      Run the RAGAS evaluation harness"
	@echo "  make test      Run the fast unit tests"
	@echo "  make lint      Run ruff"
	@echo "  make docker    Build + run the local stack (api + qdrant)"

install:
	pip install -r requirements.txt

sample:
	cp examples/sample_docs/*.txt data/raw/

qdrant:
	docker run -p 6333:6333 qdrant/qdrant

ingest:
	python -m src.ingest

index:
	python -m src.index_build

run:
	python -m src.pipeline "$(Q)"

api:
	uvicorn api.main:app --reload --port 8000

ui:
	streamlit run app/app.py

eval:
	python -m eval.run_eval

test:
	pytest -q

lint:
	ruff check .

docker:
	docker compose up --build
