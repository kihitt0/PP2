-- Create phonebook table
CREATE TABLE IF NOT EXISTS phonebook (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    phone VARCHAR(20)  NOT NULL UNIQUE
);

-- 1. Pattern-search function: search by name or phone pattern
CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.name, p.phone
        FROM phonebook p
        WHERE p.name  ILIKE '%' || pattern || '%'
           OR p.phone LIKE  '%' || pattern || '%'
        ORDER BY p.name;
END;
$$ LANGUAGE plpgsql;

-- 2. Upsert procedure: insert new contact or update phone if name already exists
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO phonebook (name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$;

-- 3. Bulk-insert procedure: insert many contacts, skip/report invalid phones
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_data TEXT[][])
LANGUAGE plpgsql AS $$
DECLARE
    rec    TEXT[];
    v_name  VARCHAR;
    v_phone VARCHAR;
BEGIN
    FOREACH rec SLICE 1 IN ARRAY p_data LOOP
        v_name  := rec[1];
        v_phone := rec[2];
        -- Validate: phone must start with + and contain only digits after it
        IF v_phone ~ '^\+[0-9]{7,15}$' THEN
            INSERT INTO phonebook (name, phone)
            VALUES (v_name, v_phone)
            ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name;
        ELSE
            RAISE NOTICE 'Invalid phone for %: %', v_name, v_phone;
        END IF;
    END LOOP;
END;
$$;

-- 4. Paginated query function: return contacts page by page
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.name, p.phone
        FROM phonebook p
        ORDER BY p.name
        LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 5. Delete procedure: remove contact by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR DEFAULT NULL,
                                            p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM phonebook WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
    ELSE
        RAISE EXCEPTION 'Provide at least one of: name or phone';
    END IF;
END;
$$;
