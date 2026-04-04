.PHONY: install lint lint:fix typecheck audit security dev build start clean

install:
	npm install

lint:
	npx next lint

lint:fix
	npx next lint --fix

typecheck:
	tsc --noEmit

audit:
	npm audit --production

audit:dev:
	npm audit

security:
	@echo "=== Security Checks ==="
	@echo "Linting..."
	@npm run lint 2>&1 || true
	@echo ""
	@echo "Type checking..."
	@npm run typecheck 2>&1 || true
	@echo ""
	@echo "Dependency audit..."
	@npm audit --audit-level=high 2>&1 || true
	@echo ""
	@echo "=== Build ==="
	@npm run build

dev:
	npm run dev

build:
	npm run build

start:
	npm run start

clean:
	rm -rf .next
	rm -rf out
	rm -rf node_modules/.cache
