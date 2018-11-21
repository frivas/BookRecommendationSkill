from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

import logging
import json
import six


ssb = StandardSkillBuilder(table_name='BookCatalogue', auto_create_table=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Prepare the source of information. This later should be a complete Catalogue
book_catalogue = get_catalogue()


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('LaunchRequest')(handler_input)
    
    def handle(self, handler_input):
        attritbutes = handler_input.attributes_manager.persistent_attributes

        if not attritbutes:
            attritbutes['topic'] = ''
            attritbutes['bookTitle'] = ''

        handler_input.attributes_manager.session_attributes = attritbutes

        output_speech = 'Hola apasionados de la lectura. ¡Bienvenidos a Planeta Recomienda!. ¿Qué temática en literatura te gusta?. Ciencia, empresas, negocios...'
        re_prompt = '¿Que tipo de literatura te gusta?. Puedes pedirme ayuda diciendo, ayuda.'

        return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).ask(re_prompt).set_should_end_session(False).response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('AMAZON.HelpIntent')(handler_input)
    
    def handle(self, handler_input):
        output_speech = 'Puedo recomendarte libros por temática, por ejemplo: Ciencia, Religión o Empresa. Para ello puedes decir: recomiéndame un libro de ciencia o dime qué libros de religión tienen. Espero esto te sirva de ayuda. Te recomiendo explorar más temáticas'

        return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


class CancelStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('AMAZON.StopIntent')(handler_input) or is_intent_name('AMAZON.CancelIntent')(handler_input)

    def handle(self, handler_input):
        output_speech = 'Gracias por utilizar Planeta Recomienda. Me tienes aquí siempre que quieras conocer nuestras novedades e incluso si ya tienes alguno en mente.'

        return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).set_should_end_session(True).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('SessionEndedRequest')(handler_input)
    
    def handle(self, handler_input):
        logger.info('La razón por la que la sesión ha terminado es: {}'.format(handler_input.request_envelop.request.reason))

        return handler_input.response_builder.response


class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        slots = handler_input.request_envelope.request.intent.slots
        for slot_name, current_slot in six.iteritems(slots):
            if current_slot.value:
                output_speech = 'En este momento no tenemos {}, si te parece escríbenos a {} y nos pondremos en contacto contigo cuando esté disponible. Lo siento.'.format(current_slot.value, 'info@planeta.es')
            else:
                output_speech = 'En este momento no tenemos lo que solicitas, si te parece escríbenos a {} y nos pondremos en contacto contigo cuando esté disponible. Lo siento.'.format('info@planeta.es')

        return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


class BookRecommendationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('BookRecommendationIntent')(handler_input)
    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        for slot_name, current_slot in six.iteritems(slots):
            if slot_name == 'topic':
                if current_slot.value:
                    logger.info(book_catalogue)
        output_speech = 'Test'

        return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


# Helper functions
def get_catalogue():
    book_catalogue_filename = 'booksList.json'
    with open(book_catalogue_filename, 'r') as book_catalogue_file:
        book_catalogue = json.load(book_catalogue_file)
    return book_catalogue


ssb.add_exception_handler(AllExceptionHandler())
ssb.add_request_handler(CancelStopIntentHandler())
ssb.add_request_handler(SessionEndedRequestHandler())
ssb.add_request_handler(LaunchRequestHandler())
ssb.add_request_handler(HelpIntentHandler())

handler = ssb.lambda_handler()