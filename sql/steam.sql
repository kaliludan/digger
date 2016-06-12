DROP TABLE steam_discount_game;

CREATE TABLE steam_discount_game(
  ID SERIAL,
  NAME TEXT NOT NULL,
  LINK TEXT NOT NULL,
  IMG_SRC TEXT,
  REVIEW TEXT,
  PRICE_BEFORE FLOAT,
  PRICE_NOW FLOAT,
  DISCOUNT CHAR(10)
);

-- Insert one example record.
INSERT INTO steam_discount_game (NAME, LINK) VALUES (
  'EXAMPLE_GAME',
  'localhost'
);
