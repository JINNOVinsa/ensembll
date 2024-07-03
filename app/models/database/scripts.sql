-- Script de renouvellement des stationnements
-- Ne par oublier d'activer les event avec `set global event_scheduler=on`

DROP EVENT IF EXISTS resetCustomWeekBookings;

DELIMITER ;;

CREATE EVENT resetCustomWeekBookings ON SCHEDULE EVERY 7 DAY STARTS '2023-02-26 23:59:59' DO BEGIN
  -- This execute every Sunday night and reset custom week bookings based on custom reset amount
  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 7 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onMonday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 7 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onMonday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 1 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onTuesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 1 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onTuesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 2 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onWednesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 2 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onWednesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 3 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onThursday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 3 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onThursday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 4 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onFriday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 4 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onFriday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 5 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSaturday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 5 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSaturday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

  UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 6 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSunday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
  UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 6 - WEEKDAY(startTS) + 7 * (customAmount-1) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSunday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

END ;;

DELIMITER ;


DROP EVENT IF EXISTS refreshBookings;

DELIMITER ;;

CREATE EVENT refreshBookings ON SCHEDULE EVERY 1 DAY STARTS '2023-02-22 11:50:40' DO BEGIN

    -- Update daily Bookings
    UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 24 hour) WHERE repeatInterval="daily" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
    UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 24 hour) WHERE repeatInterval="daily" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

    -- Update weekly Bookings
    UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 7 day) WHERE repeatInterval="weekly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
    UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 7 day) WHERE repeatInterval="weekly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

    -- Update monthly Bookings
    UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 1 month) WHERE repeatInterval="monthly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
    UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 1 month) WHERE repeatInterval="monthly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

    -- Update custom daily Bookings
    UPDATE Bookings SET startTS=date_add(startTS, INTERVAL customAmount day) WHERE repeatInterval="custom" AND customInterval="day" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
    UPDATE Bookings SET endTS=date_add(endTS, INTERVAL customAmount day) WHERE repeatInterval="custom" AND customInterval="day" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

    -- Update custom monthly Bookings
    UPDATE Bookings SET startTS=date_add(startTS, INTERVAL customAmount month) WHERE repeatInterval="custom" AND customInterval="month" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
    UPDATE Bookings SET endTS=date_add(endTS, INTERVAL customAmount month) WHERE repeatInterval="custom" AND customInterval="month" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;

    -- Update custom weekly Bookings during week
    -- As monday is the first day of week, if a booking is made on monday it's reset on sunday and never refreshed

    -- Tuesday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=1
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 1 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onTuesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 1 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onTuesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;

    -- Wednesday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=2
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 2 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onWednesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 2 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onWednesday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;

    -- Thursday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=3
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 3 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onThursday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 3 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onThursday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;

    -- Friday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=4
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 4 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onFriday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 4 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onFriday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;

    -- Saturday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=5
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 5 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSaturday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 5 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSaturday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;

    -- Sunday
    IF SELECT(WEEKDAY(CURRENT_TIMESTAMP))=6
      BEGIN
        UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 6 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSunday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
        UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 6 - WEEKDAY(startTS) DAY) WHERE repeatInterval="custom" AND customInterval="week" AND onSunday=1 AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP;
      END
    END IF;
END ;;

DELIMITER ;






DELIMITER ;;

CREATE PROCEDURE tep()
BEGIN
DECLARE length INT DEFAULT 0;
DECLARE counter INT DEFAULT 0;
SELECT COUNT(*) FROM TestTable INTO length;
SET counter=0;
WHILE counter<length DO
  SELECT id FROM TestTable LIMIT counter,1;
  DISPLAY;
  SET counter = counter + 1;
END WHILE;
End;
;;

DELIMITER ;