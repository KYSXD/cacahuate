import json
import pika
from coralillo.errors import ModelNotFoundError

from .logger import log
from .xml import Xml
from .errors import ProcessNotFound, CannotMove
from .node import make_node, Node, AsyncNode
from .models import Execution, Pointer


class Handler:
    ''' The actual process machine, it is in charge of moving the pointers
    among the graph of nodes '''

    def __init__(self, config):
        self.config = config

    def __call__(self, channel, method, properties, body:bytes):
        ''' the main callback of the PVM '''
        message = self.parse_message(body)

        try:
            to_notify = self.call(message)
        except ModelNotFoundError as e:
            return log.error(str(e))
        except CannotMove as e:
            return log.error(str(e))

        for pointer in to_notify:
            channel.basic_publish(
                exchange = '',
                routing_key = self.config['RABBIT_QUEUE'],
                body = json.dumps({
                    'command': 'step',
                    'pointer_id': pointer.id,
                }),
                properties = pika.BasicProperties(
                    delivery_mode = 2, # make message persistent
                ),
            )

        if not self.config['RABBIT_NO_ACK']:
            channel.basic_ack(delivery_tag = method.delivery_tag)

    def call(self, message:dict):
        execution, pointer, xmliter, current_node = self.recover_step(message)
        log.debug('Recovered {proc} at {cls} {node}'.format(
            proc = execution.process_name,
            cls = type(current_node).__name__,
            node = pointer.node_id,
        ))

        pointers = [] # pointers to be notified back
        data = message['data'] if 'data' in message else dict()

        # This call raises an exception if data doesn't have enough information
        current_node.validate(data)

        pointer.delete()
        next_nodes = current_node.next(xmliter, data)

        for node in next_nodes:
            node()

            if not node.is_end():
                pointer = self.create_pointer(node, execution)

                if isinstance(node, AsyncNode):
                    log.debug('execution waiting at {cls} {node_id}'.format(
                        cls = type(node).__name__,
                        node_id = pointer.id,
                    ))
                else:
                    pointers.append(pointer)
            else:
                log.debug('Branch of {proc} ended at {node}'.format(
                    proc = execution.process_name,
                    node = node.id,
                ))

        if execution.proxy.pointers.count() == 0:
            execution.delete()
            log.debug('Execution {exc} finished'.format(
                exc = execution.id,
            ))

        return pointers

    def parse_message(self, body:bytes):
        ''' validates a received message against all possible needed fields
        and structure '''
        try:
            message = json.loads(body)
        except json.decoder.JSONDecodeError:
            raise ValueError('Message is not json')

        if 'command' not in message:
            raise KeyError('Malformed message: must contain command keyword')

        if message['command'] not in self.config['COMMANDS']:
            raise ValueError('Command not supported: {}'.format(
                message['command']
            ))

        return message

    def create_pointer(self, node:Node, execution:Execution):
        ''' Given a node, its process, and a specific execution of the former
        create a persistent pointer to the current execution state '''
        pointer =  Pointer.validate(node_id=node.id).save()
        pointer.proxy.execution.set(execution)

        return pointer

    def recover_step(self, message):
        ''' given an execution id and a pointer from the persistent storage,
        return the asociated process node to continue its execution '''
        if 'pointer_id' not in message:
            raise KeyError('Requested step without pointer id')

        pointer = Pointer.get_or_exception(message['pointer_id'])
        execution = pointer.proxy.execution.get()
        xml = Xml.load(self.config, execution.process_name)

        assert execution.process_name == xml.name, 'Inconsisten pointer found'

        point = xml.find(
            lambda e:'id' in e.attrib and e.attrib['id'] == pointer.node_id
        )

        return execution, pointer, xml, make_node(point)
