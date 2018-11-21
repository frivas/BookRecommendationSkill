from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core import attributes_manager
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, request_envelope
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Slot, SlotConfirmationStatus, DialogState
from ask_sdk_model.slu.entityresolution import StatusCode

import logging
import json
import six


ssb = StandardSkillBuilder(table_name='BookCatalogue', auto_create_table=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Helper functions
def get_catalogue():
    book_catalogue_filename = 'booksList.json'
    with open(book_catalogue_filename, 'r') as book_catalogue_file:
        book_catalogue = json.load(book_catalogue_file)
    return book_catalogue


# Prepare the source of information. This later should be a complete Catalogue
book_catalogue = get_catalogue()


@ssb.request_handler(can_handle_func=is_request_type('LaunchRequest'))
def launch_request_handler(handler_input):
    attritbutes = handler_input.attributes_manager.persistent_attributes

    if not attritbutes:
        attritbutes['topic'] = ''
        attritbutes['bookTitle'] = ''

    handler_input.attributes_manager.session_attributes = attritbutes

    output_speech = 'Hola apasionados de la lectura. ¡Bienvenidos a Planeta Recomienda!. ¿Qué temática en literatura te gusta?. Ciencia, empresas, negocios...'
    re_prompt = '¿Que tipo de literatura te gusta?. Puedes pedirme ayuda diciendo, ayuda.'

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).ask(re_prompt).set_should_end_session(False).response


@ssb.request_handler(can_handle_func=is_intent_name('AMAZON.HelpIntent'))
def help_request_handler(handler_input):
    output_speech = 'Puedo recomendarte libros por temática, por ejemplo: Ciencia, Religión o Empresa. Para ello puedes decir: recomiéndame un libro de ciencia o dime qué libros de religión tienen. Espero esto te sirva de ayuda. Te recomiendo explorar más temáticas'

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


@ssb.request_handler(can_handle_func=lambda input: is_intent_name('AMAZON.StopIntent')(input) or
                     is_intent_name('AMAZON.CancelIntent')(input))
def stop_cancel_intent_handler(handler_input):
    output_speech = 'Gracias por utilizar Planeta Recomienda. Me tienes aqui siempre que quieras conocer nuestras novedades e incluso si ya tienes alguno en mente.'

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).set_should_end_session(True).response


@ssb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    logger.info('La razón por la que la sesión ha terminado es: {}'.format(handler_input.request_envelop.request.reason))

    return handler_input.response_builder.response


@ssb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    slots = handler_input.request_envelope.request.intent.slots
    for slot_name, current_slot in six.iteritems(slots):
        if current_slot.value:
            output_speech = 'En este momento no tenemos {}, si te parece escríbenos a {} y nos pondremos en contacto contigo cuando esté disponible. Lo siento.'.format(current_slot.value, 'info@planeta.es')
        else:
            output_speech = 'En este momento no tenemos lo que solicitas, si te parece escríbenos a {} y nos pondremos en contacto contigo cuando esté disponible. Lo siento.'.format('info@planeta.es')

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


@ssb.request_handler(can_handle_func=is_intent_name('BookRecommendationIntent'))
def book_recommendation_intent_handler(handler_input):
    slots = handler_input.request_envelope.request.intent.slots
    for slot_name, current_slot in six.iteritems(slots):
        if slot_name == 'topic':
            if current_slot.value:
                logger.info(book_catalogue)
    output_speech = 'Test'
    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


handler = ssb.lambda_handler()
