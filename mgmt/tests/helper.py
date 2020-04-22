import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def do_add_remove_maglev(test, table, add, remove, exp_table):
    if add:
        logger.info("Adding {} to the table.".format(add))
        table.add(add)
    if remove:
        logger.info("Removing {} from the table.".format(remove))
        table.remove(remove)
    act_table = table.get_table()
    test.assertEqual(exp_table, act_table)
