DELIMITER //

CREATE FUNCTION find_sum_posts() RETURNS INT
BEGIN
  RETURN (SELECT COUNT(*) FROM posts);
END //

DELIMITER ;

CREATE PROCEDURE go_to_rules_page()
BEGIN
  SELECT CONCAT('/rules');
END //

DELIMITER ;
