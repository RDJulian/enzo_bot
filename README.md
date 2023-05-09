# EnzoBot

<p align="center">
  <img width="50%" height="50%" src="images/sirius_black.png" alt="La gorda matosa"><br>
Simple Discord Bot for counting days since "The Accident"
</p>

## Version 2.0 Patch Notes

Enzo now counts with 3 main modules:

1. Keyword Counter: Enzo will read all messages and try to match all words to a predetermined set of words. If any is
   mentioned, Enzo will add one to it's counter. All words can be displayed in descending count order with a command.
   This set of words can grow if given specified triggers (i.e. pup will add puppy to the set).
2. Response on Keyword: Enzo will respond in a specified way when it matches words to keywords, similar to Keyword
   Counter functionality.
3. Accident Day Message Updater: Enzo will automatically modify the Accident Message every day at a fixed time. This
   timer can be manually manipulated via 5 commands:
    1. !refrescar: Refreshes the message.
    2. !reiniciar: Resets the message.
    3. !modificar_hora: Modifies the update time.
    4. !modificar_dias: Modifies the day counter.