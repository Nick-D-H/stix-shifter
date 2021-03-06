from stix_shifter_utils.utils.base_entry_point import BaseEntryPoint

class EntryPoint(BaseEntryPoint):

    def __init__(self, connection={}, configuration={}, options={}):
        super().__init__(options)
        self.set_async(False)
        #TODO add test cases

        if connection:
            self.setup_transmission_simple(connection, configuration)
        else:
            self.setup_translation_simple(dialect_default='default')