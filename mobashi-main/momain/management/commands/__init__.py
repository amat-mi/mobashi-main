# -*- coding: utf-8 -*-

import ast
import json
import os

from django.core.files.base import ContentFile
from django.core.management.base import CommandError, LabelCommand
from django.db import transaction


class BaseLabelCommand(LabelCommand):
    help_command = u''
    help_descr = u''
    DJANGO_QUIET = None

    def __init__(self):
        self.help = self.help + self.help_descr
        super(BaseLabelCommand, self).__init__()

    def printline(self, msg):
        if self.DJANGO_QUIET is None:
            self.DJANGO_QUIET = ast.literal_eval(
                os.getenv('DJANGO_QUIET', 'False'))

        if not self.DJANGO_QUIET:  # only if not requested otherwise
            self.stdout.write(u'{}\n'.format(msg))

    def printjson(self, data):
        self.stdout.write(u'{}\n'.format(json.dumps(
            data, sort_keys=True, indent=4, separators=(',', ': '))))

    def handle(self, *labels, **options):
        self.stdout.write(self.usage(self.help_command))
        super(BaseLabelCommand, self).handle(*labels, **options)


class RedoRoutingCommand(BaseLabelCommand):
    first_label = None
    help_descr = u'''
    '''

    def handle(self, *labels, **options):
        l = len(labels or [])

        self.printline(u'Inizio {}'.format(labels))
#     transaction.commit_unless_managed()
#     transaction.enter_transaction_management()
#     transaction.managed(True)
        try:
            mode = labels[0] if l > 0 else None
            self.do_it(mode)
#       transaction.commit()
            self.printline('Fine')
        except Exception as exc:
            #       transaction.rollback()
            raise CommandError(exc)
        finally:
            #       transaction.leave_transaction_management()
            pass


class HarvestCommand(BaseLabelCommand):
    first_label = None
    help_descr = u'''
    '''

    def handle(self, *labels, **options):
        l = len(labels or [])

        self.printline(u'Inizio {}'.format(labels))
        try:
            with transaction.atomic():
                doasync = labels[0].upper() == 'ASYNC' if l > 0 else False
                self.do_it(doasync)
                self.printline('Fine')
        except Exception as exc:
            transaction.rollback()
            raise CommandError(exc)
