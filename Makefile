up:
	docker compose up -d --build
 
down:
	docker compose down
 
test:
	@echo "--- Testes unitários ---"
	docker compose exec api pytest tests/ -v
 
	@echo "\n--- Contrato: pergunta com contexto ---"
	curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"O que é composição?"}' | python3 -m json.tool
 
	@echo "\n--- Contrato: fallback ---"
	curl -s -X POST http://localhost:8000/messages \
	  -H "Content-Type: application/json" \
	  -d '{"message":"Qual a previsão do tempo amanhã?"}' | python3 -m json.tool