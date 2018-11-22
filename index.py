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
import random


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

    attributes = handler_input.attributes_manager.persistent_attributes

    if not attributes:
        attributes['topic'] = ''
        attributes['title'] = ''

    handler_input.attributes_manager.session_attributes = attributes

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

    logger.info(f'La razón por la que la sesión ha terminado es: {handler_input.request_envelop.request.reason}')

    return handler_input.response_builder.response


@ssb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):

    logger.info('Ha habido el siguiente problema {}'.format(exception))
    output_speech = 'Perdona, no he entendido lo que me has dicho. ¿Te importaría repetir?'

    return handler_input.response_builder.speak(output_speech).response


@ssb.request_handler(can_handle_func=is_intent_name('BookRecommendationIntent'))
def book_recommendation_intent_handler(handler_input):
    slots = handler_input.request_envelope.request.intent.slots
    attributes = handler_input.attributes_manager.session_attributes

    for slot_name, current_slot in six.iteritems(slots):
        if slot_name == 'topic':
            # All the events have a Resolutions Per Authority except the one without a value for a slot
            # In this case I support an empty slot because if it is I just select a random book
            if current_slot.resolutions and current_slot.resolutions.resolutions_per_authority[0]:
                # Once I know the slot is not empty I check if there is a MATCH or not
                if current_slot.resolutions.resolutions_per_authority[0].status.code == StatusCode.ER_SUCCESS_MATCH:

                    topic = current_slot.resolutions.resolutions_per_authority[0].values[0].value.name

                    if topic.capitalize() in book_catalogue.keys():
                        random_book = random.choice(book_catalogue[topic.capitalize()])

                        output_speech = f'He encontrado un libro que podría ser interesante. Tiene muy buenas opiniones. Su título es {random_book["title"]} de {random_book["author"]}. ¿Quieres saber más sobre el libro?.'
                        re_prompt = '¿Quieres saber más sobre este libro?'
                        
                        attributes['topic'] = topic
                        attributes['title'] = random_book['title']
                        persist_attributes(handler_input, attributes)
                # If there is no match we inform the user we do not have the requested topic
                else:
                    output_speech = f'Lo siento, ahora mismo no tenemos nada relacionado a {"info@planeta.es"}. Si te parece escribenos a la dirección de correo electrónico que te envío a la aplicación y nos pondremos en contacto contigo tan pronto tengamos disponibilidad'
                    re_prompt = '¿Quieres que busque algún otro libro de otra temática?'

            # if there is no Resolutions Per Authority it means the slot is empty and we just need to generate a random book
            else:
                topic = random.choice(list(book_catalogue.keys()))
                random_book = random.choice(book_catalogue[topic])

                output_speech = f'He encontrado un libro que podría ser interesante. Tiene muy buenas opiniones. Su título es {random_book["title"]} de {random_book["author"]}. ¿Quieres saber más sobre el libro?.'
                re_prompt = '¿Quieres saber más sobre este libro?'

                attributes['topic'] = topic
                attributes['title'] = random_book['title']
                persist_attributes(handler_input, attributes)

    return handler_input.response_builder.speak(output_speech).ask(re_prompt).set_card(SimpleCard('Planeta Recomienda', output_speech)).response


@ssb.request_handler(can_handle_func=is_intent_name("AMAZON.YesIntent"))
def yes_intent_handler(handler_input):
    attributes = handler_input.attributes_manager.session_attributes

    book_info = [info for info in book_catalogue[attributes['topic']] if info['title'] == attributes['title']]
    print(book_info)

    output_speech = f'{book_info[0]["title"]} se trata de {book_info[0]["synopsis"]}. Te envío información a la aplicación.'

    card_info = f'{book_info[0]["title"]} de {book_info[0]["author"]} de la colección {book_info[0]["collection"]} por {book_info[0]["price"]}'

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', card_info)).response


@ssb.request_handler(can_handle_func=is_intent_name("AMAZON.NoIntent"))
def no_intent_handler(handler_input):
    output_speech = 'Muchas gracias por utilizar Planeta Recomienda. Siempre puedes visitar nuestra página web o ponerte en contacto con nosotros por teléfono o correo electrónico, estaremos contentos de atenderte. Te envío nuestra información de contacto a la aplicación. ¡Hasta Pronto!'

    card_info = f'Nuestra Web {"https://www.planeta.es/es"}. Teléfono: {"914 23 37 04"}. Correo Electrónico: {"info@planeta.es"}'

    return handler_input.response_builder.speak(output_speech).set_card(SimpleCard('Planeta Recomienda', card_info)).response

def persist_attributes(handler_input, attr):
    attributes = handler_input.attributes_manager.session_attributes

    attributes['topic'] = attr['topic']
    attributes['title'] = attr['title']

    handler_input.attributes_manager.session_attributes = attributes
    handler_input.attributes_manager.persistent_attributes = attributes
    handler_input.attributes_manager.save_persistent_attributes()

handler = ssb.lambda_handler()
