CREATE TABLE bill_categories (
  id SERIAL PRIMARY KEY
  , category_name TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE bill_categories IS 'unique names of categories of bills';

CREATE TABLE bill_categories_join
(
  bill_id int NOT NULL,
  bill_category_id int NOT NULL,
  CONSTRAINT bill_categories_join__bill_id_fk
    FOREIGN KEY (bill_id) REFERENCES bills (id),
  CONSTRAINT bill_categories_join__category_id_fk
    FOREIGN KEY (bill_category_id) REFERENCES bill_categories (id),
  PRIMARY KEY (bill_id, bill_category_id)
);
COMMENT ON TABLE bill_categories_join IS 'joins bills to their bill_categories';
