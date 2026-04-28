-- TSIS 1 – PhoneBook stored procedures and functions

-- ─── Function: add_phone ─────────────────────────────────────────────────────
-- Adds a phone number to an existing contact.

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


-- ─── Function: move_to_group ──────────────────────────────────────────────────
-- Moves a contact to a group; creates the group if it does not exist.

CREATE OR REPLACE FUNCTION move_to_group(
    p_contact_id INTEGER,
    p_group_name VARCHAR
) RETURNS VOID AS $$
DECLARE
    gid INTEGER;
BEGIN
    INSERT INTO pb_groups(name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO gid FROM pb_groups WHERE name = p_group_name;
    UPDATE pb_contacts SET group_id = gid WHERE id = p_contact_id;
END;
$$ LANGUAGE plpgsql;


-- ─── Function: search_contacts ────────────────────────────────────────────────
-- Full-text search across name, email, and all phone numbers.

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
