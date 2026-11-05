/* Banco de Dados Lógico 2 - TCC 1: */

CREATE TABLE usuario (
    id_usuario NUMERIC PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    senha VARCHAR(255),
    status VARCHAR,
    nivel_permissao NUMERIC
);

CREATE TABLE produto (
    nome VARCHAR(100),
    preco_venda NUMERIC,
    estoque_minimo NUMERIC,
    estoque_maximo NUMERIC,
    estoque_atual NUMERIC,
    descricao VARCHAR(100),
    codigo_sku NUMERIC,
    id_produto NUMERIC PRIMARY KEY
);

CREATE TABLE fornecedor (
    id_fornecedor NUMERIC PRIMARY KEY,
    nome VARCHAR(100),
    cnpj VARCHAR(14),
    telefone VARCHAR(11),
    email VARCHAR(100)
);

CREATE TABLE estoque (
    id_estoque NUMERIC PRIMARY KEY,
    localizacao VARCHAR
);

CREATE TABLE movimentacao_estoque (
    id_movimentacao NUMERIC PRIMARY KEY,
    tipo VARCHAR,
    quantidade NUMERIC,
    motivo VARCHAR,
    data_hora TIMESTAMP,
    fk_usuario_id_usuario NUMERIC
);

CREATE TABLE pedido_venda (
    id_pedido NUMERIC PRIMARY KEY,
    data_pedido DATE,
    tipo VARCHAR,
    status VARCHAR,
    valor_atual NUMERIC
);

CREATE TABLE item_pedido (
    id_item NUMERIC PRIMARY KEY,
    quantidade NUMERIC,
    valor_unitario NUMERIC
);

CREATE TABLE pagamento (
    id_pagamento NUMERIC PRIMARY KEY,
    forma_pagamento VARCHAR,
    valor NUMERIC,
    parcela NUMERIC,
    data_pagamento DATE,
    fk_pedido_venda_id_pedido NUMERIC
);

CREATE TABLE nota_fiscal (
    id_nota NUMERIC PRIMARY KEY,
    numero_nota NUMERIC,
    tipo_nota VARCHAR,
    data_emissao DATE,
    xml VARCHAR,
    fk_pedido_venda_id_pedido NUMERIC
);

CREATE TABLE pedido_compra (
    id_pedido_compra NUMERIC PRIMARY KEY,
    data_pedido DATE,
    previsao_entrega DATE,
    status VARCHAR
);

CREATE TABLE cotacao (
    id_cotacao NUMERIC PRIMARY KEY,
    prazo_validade DATE,
    data_criacao DATE,
    fk_fornecedor_id_fornecedor NUMERIC
);

CREATE TABLE auditoria (
    id_auditoria NUMERIC PRIMARY KEY,
    data_hora TIMESTAMP,
    acao_realizada VARCHAR,
    ip NUMERIC(255),
    dados_antes VARCHAR,
    dados_depois VARCHAR,
    fk_usuario_id_usuario NUMERIC
);

CREATE TABLE gerencia (
    fk_movimentacao_estoque_id_movimentacao NUMERIC,
    fk_produto_id_produto NUMERIC
);

CREATE TABLE fornece (
    fk_fornecedor_id_fornecedor NUMERIC,
    fk_produto_id_produto NUMERIC
);

CREATE TABLE possui (
    fk_produto_id_produto NUMERIC,
    fk_item_pedido_id_item NUMERIC
);

CREATE TABLE possui (
    fk_pedido_venda_id_pedido NUMERIC,
    fk_item_pedido_id_item NUMERIC
);

CREATE TABLE convoca (
    fk_pedido_compra_id_pedido_compra NUMERIC,
    fk_fornecedor_id_fornecedor NUMERIC
);
 
ALTER TABLE movimentacao_estoque ADD CONSTRAINT FK_movimentacao_estoque_2
    FOREIGN KEY (fk_usuario_id_usuario)
    REFERENCES usuario (id_usuario)
    ON DELETE CASCADE;
 
ALTER TABLE pagamento ADD CONSTRAINT FK_pagamento_2
    FOREIGN KEY (fk_pedido_venda_id_pedido)
    REFERENCES pedido_venda (id_pedido)
    ON DELETE CASCADE;
 
ALTER TABLE nota_fiscal ADD CONSTRAINT FK_nota_fiscal_2
    FOREIGN KEY (fk_pedido_venda_id_pedido)
    REFERENCES pedido_venda (id_pedido)
    ON DELETE CASCADE;
 
ALTER TABLE cotacao ADD CONSTRAINT FK_cotacao_2
    FOREIGN KEY (fk_fornecedor_id_fornecedor)
    REFERENCES fornecedor (id_fornecedor)
    ON DELETE RESTRICT;
 
ALTER TABLE auditoria ADD CONSTRAINT FK_auditoria_2
    FOREIGN KEY (fk_usuario_id_usuario)
    REFERENCES usuario (id_usuario)
    ON DELETE CASCADE;
 
ALTER TABLE gerencia ADD CONSTRAINT FK_gerencia_1
    FOREIGN KEY (fk_movimentacao_estoque_id_movimentacao)
    REFERENCES movimentacao_estoque (id_movimentacao)
    ON DELETE RESTRICT;
 
ALTER TABLE gerencia ADD CONSTRAINT FK_gerencia_2
    FOREIGN KEY (fk_produto_id_produto)
    REFERENCES produto (id_produto)
    ON DELETE RESTRICT;
 
ALTER TABLE fornece ADD CONSTRAINT FK_fornece_1
    FOREIGN KEY (fk_fornecedor_id_fornecedor)
    REFERENCES fornecedor (id_fornecedor)
    ON DELETE RESTRICT;
 
ALTER TABLE fornece ADD CONSTRAINT FK_fornece_2
    FOREIGN KEY (fk_produto_id_produto)
    REFERENCES produto (id_produto)
    ON DELETE SET NULL;
 
ALTER TABLE possui ADD CONSTRAINT FK_possui_1
    FOREIGN KEY (fk_produto_id_produto)
    REFERENCES produto (id_produto)
    ON DELETE RESTRICT;
 
ALTER TABLE possui ADD CONSTRAINT FK_possui_2
    FOREIGN KEY (fk_item_pedido_id_item)
    REFERENCES item_pedido (id_item)
    ON DELETE RESTRICT;
 
ALTER TABLE possui ADD CONSTRAINT FK_possui_1
    FOREIGN KEY (fk_pedido_venda_id_pedido)
    REFERENCES pedido_venda (id_pedido)
    ON DELETE RESTRICT;
 
ALTER TABLE possui ADD CONSTRAINT FK_possui_2
    FOREIGN KEY (fk_item_pedido_id_item)
    REFERENCES item_pedido (id_item)
    ON DELETE RESTRICT;
 
ALTER TABLE convoca ADD CONSTRAINT FK_convoca_1
    FOREIGN KEY (fk_pedido_compra_id_pedido_compra)
    REFERENCES pedido_compra (id_pedido_compra)
    ON DELETE RESTRICT;
 
ALTER TABLE convoca ADD CONSTRAINT FK_convoca_2
    FOREIGN KEY (fk_fornecedor_id_fornecedor)
    REFERENCES fornecedor (id_fornecedor)
    ON DELETE RESTRICT;