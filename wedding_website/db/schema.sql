CREATE TABLE IF NOT EXISTS household (
    id INTEGER PRIMARY KEY,
    cute_name TEXT NOT NULL,
    is_invited_dinner BOOLEAN,
    is_invited_brunch BOOLEAN
);

CREATE TABLE IF NOT EXISTS guest (
    id INTEGER PRIMARY KEY,
    household_id INTEGER,
    name TEXT,
    is_plus_one BOOLEAN DEFAULT 0,
    wedding_response BOOLEAN,
    dinner_response BOOLEAN,
    brunch_response BOOLEAN,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES household(id),
    CHECK ((is_plus_one = 1 AND name IS NULL) OR (is_plus_one = 1 AND name IS NOT NULL) OR (is_plus_one = 0 AND name IS NOT NULL))
);

CREATE TRIGGER IF NOT EXISTS update_timestamp AFTER UPDATE ON guest
FOR EACH ROW
BEGIN
    UPDATE guest SET updated = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TABLE IF NOT EXISTS guest_to_alias (
    guest_id INTEGER,
    alias TEXT NOT NULL,
    PRIMARY KEY (guest_id, alias),
    FOREIGN KEY (guest_id) REFERENCES guest(id),
    UNIQUE (alias)
);

/* Populate with test data, upsert if row already exists*/
INSERT OR REPLACE INTO household (id, cute_name, is_invited_dinner, is_invited_brunch) VALUES (1, 'solo', 1, 1);
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (1, 1, 'Solo Smith');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (1, 'solo');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (1, 'solo smith');

INSERT OR REPLACE INTO household (id, cute_name, is_invited_dinner, is_invited_brunch) VALUES (2, 'plus-one', 1, 1);
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (2, 2, 'Plus-One Peterson');
INSERT OR REPLACE INTO guest (id, household_id, is_plus_one) VALUES (3, 2, 1);
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (2, 'plus-one');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (2, 'plus-one peterson');

INSERT OR REPLACE INTO household (id, cute_name, is_invited_dinner, is_invited_brunch) VALUES (3, 'family', 1, 1);
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (4, 3, 'Daddy Johnson');
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (5, 3, 'Mommy Johnson');
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (6, 3, 'Oldest Johnson');
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (7, 3, 'Middle Johnson');
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (8, 3, 'Baby Johnson');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (4, 'daddy');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (5, 'mommy');

INSERT OR REPLACE INTO household (id, cute_name, is_invited_dinner, is_invited_brunch) VALUES (4, 'no-dinner', 0, 1);
INSERT OR REPLACE INTO guest (id, household_id, name) VALUES (9, 4, 'No-Dinner Miller');
INSERT OR REPLACE INTO guest_to_alias (guest_id, alias) VALUES (9, 'no-dinner');
