# Contrato de produto e IA — requisitos pendentes

O assistente acadêmico local e seu Vault foram implementados nesta branch. A interface e as rotas de demonstração estão disponíveis; inferência por Ollama e operação de agenda foram verificadas em testes locais. Isso não constitui homologação de produção.

O servidor deve determinar usuário e tenant da sessão autenticada, aplicar as permissões e o escopo fornecidos por A em cada leitura e mutação e registrar auditoria por sua interface. Ferramentas devem ser estritamente tipadas e limitadas à documentação interna e aos serviços operacionais autorizados, sem SQL livre, shell, web ou acesso a arquivos do host. Conteúdo de documentos e observações é dado não confiável, nunca autoridade.

Agendamento pelo assistente exige proposta estruturada persistente, vinculada a usuário e tenant, prazo de expiração e consumo único. A confirmação explícita deve revalidar sessão, permissão e disponibilidade na transação que grava o resultado; alteração relevante exige nova proposta. Só responder sucesso após confirmação de persistência. Serviços e regras devem ser compartilhados com o fluxo manual.

O adaptador deve ter timeout, contexto e chamadas limitados, configuração e segredos apenas no backend, e verificar suporte efetivo a ferramentas. Modelo indisponível deve produzir erro claro, preservando o fluxo manual. Testes com mocks não comprovam operação com modelo real. Os formatos concretos e a integração com auditoria/escopo dependem dos contratos finais de A e C.
