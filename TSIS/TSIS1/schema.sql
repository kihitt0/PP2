-- TSIS 1 – PhoneBook extended schema
-- Run once to set up all tables and stored procedures/functions.

-- ─── Tables ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS pb_groups (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(80) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pb_contacts (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150),
    birthday   DATE,
    group_id   INTEGER REFERENCES pb_groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pb_phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES pb_contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(30) NOT NULL,
    kind       VARCHAR(10) NOT NULL DEFAULT 'mobile'
                   CHECK (kind IN ('home','work','mobile'))
);

-- ─── Function: add_phone ─────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION add_phone(
    p_contact_id INTEGER,
    p_phone      VARCHAR,
    p_kind       VARCHAR DEFAULT 'mobile'
) RETURNS VOID AS $$
BEGIN
    INSERT INTO pb_phones(contact_id, phone, kind)
    VALUES (p_contact_id, p_phone, p_kind);
END;
$$ LANGUAGE plpgsql;

-- ─── Function: move_to_group ────────────────────────────────────────────

CREATE OR REPLACE FUNCTION move_to_group(
    p_contact_id INTEGER,
    p_group_name VARCHAR
) RETURNS VOID AS $$
DECLARE
    gid INTEGER;
BEGIN
    -- Create group if it doesn't exist
    INSERT INTO pb_groups(name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO gid FROM pb_groups WHERE name = p_group_name;
    UPDATE pb_contacts SET group_id = gid WHERE id = p_contact_id;
END;
$$ LANGUAGE plpgsql;

-- ─── Function: search_contacts ──────────────────────────────────────────

CREATE OR REPLACE FUNCTION search_contacts(p_pattern VARCHAR)
RETURNS TABLE(
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name  AS grp,
        STRING_AGG(p.phone || ' (' || p.kind || ')', ', '
                   ORDER BY p.kind) AS phones
    FROM pb_contacts c
    LEFT JOIN pb_groups g  ON g.id  = c.group_id
    LEFT JOIN pb_phones  p ON p.contact_id = c.id
    WHERE c.name  ILIKE '%' || p_pattern || '%'
       OR c.email ILIKE '%' || p_pattern || '%'
       OR p.phone ILIKE '%' || p_pattern || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;
