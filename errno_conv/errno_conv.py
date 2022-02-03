#!/usr/bin/env python3

# Description: Python ERRNO converter
# Author: dherslof

import argparse
import errno
from itertools import count
import os
from typing import Counter

class ErrorHndlr:
   def __init__(self):
      self.err_code_description_map = errno.errorcode
      self.err_str = [  'EPERM',
                        'ENOENT',
                        'ESRCH',
                        'EINTR',
                        'EIO',
                        'ENXIO',
                        'E2BIG',
                        'ENOEXEC',
                        'EBADF',
                        'ECHILD',
                        'EAGAIN',
                        'ENOMEM',
                        'EACCES',
                        'EFAULT',
                        'ENOTBLK',
                        'EBUSY',
                        'EEXIST',
                        'EXDEV',
                        'ENODEV',
                        'ENOTDIR',
                        'EISDIR',
                        'EINVAL',
                        'ENFILE',
                        'EMFILE',
                        'ENOTTY',
                        'ETXTBSY',
                        'EFBIG',
                        'ENOSPC',
                        'ESPIPE',
                        'EROFS',
                        'EMLINK',
                        'EPIPE',
                        'EDOM',
                        'ERANGE',
                        'EDEADLCK',
                        'ENAMETOOLONG',
                        'ENOLCK',
                        'ENOSYS',
                        'ENOTEMPTY',
                        'ELOOP',
                        'EWOULDBLOCK',
                        'ENOMSG',
                        'EIDRM',
                        'ECHRNG',
                        'EL2NSYNC',
                        'EL3HLT',
                        'EL3RST',
                        'ELNRNG',
                        'EUNATCH',
                        'ENOCSI',
                        'EL2HLT',
                        'EBADE',
                        'EBADR',
                        'EXFULL',
                        'ENOANO',
                        'EBADRQC',
                        'EBADSLT',
                        'EDEADLOCK',
                        'EBFONT',
                        'ENOSTR',
                        'ENODATA',
                        'ETIME',
                        'ENOSR',
                        'ENONET',
                        'ENOPKG',
                        'EREMOTE',
                        'ENOLINK',
                        'EADV',
                        'ESRMNT',
                        'ECOMM',
                        'EPROTO',
                        'EMULTIHOP',
                        'EDOTDOT',
                        'EBADMSG',
                        'EOVERFLOW',
                        'ENOTUNIQ',
                        'EBADFD',
                        'EREMCHG',
                        'ELIBACC',
                        'ELIBBAD',
                        'ELIBSCN',
                        'ELIBMAX',
                        'ELIBEXEC',
                        'EILSEQ',
                        'ERESTART',
                        'ESTRPIPE',
                        'EUSERS',
                        'ENOTSOCK',
                        'EDESTADDRREQ',
                        'EMSGSIZE',
                        'EPROTOTYPE',
                        'ENOPROTOOPT',
                        'EPROTONOSUPPORT',
                        'ESOCKTNOSUPPORT',
                        'ENOTSUP',
                        'EOPNOTSUPP',
                        'EPFNOSUPPORT',
                        'EAFNOSUPPORT',
                        'EADDRINUSE',
                        'EADDRNOTAVAIL',
                        'ENETDOWN',
                        'ENETUNREACH',
                        'ENETRESET',
                        'ECONNABORTED',
                        'ECONNRESET',
                        'ENOBUFS',
                        'EISCONN',
                        'ENOTCONN',
                        'ESHUTDOWN',
                        'ETOOMANYREFS',
                        'ETIMEDOUT',
                        'ECONNREFUSED',
                        'EHOSTDOWN',
                        'EHOSTUNREACH',
                        'EALREADY',
                        'EINPROGRESS',
                        'ESTALE',
                        'EUCLEAN',
                        'ENOTNAM',
                        'ENAVAIL',
                        'EISNAM',
                        'EREMOTEIO',
                        'EDQUOT',
                        'ECANCELED',
                        'EKEYEXPIRED',
                        'EKEYREJECTED',
                        'EKEYREVOKED',
                        'EMEDIUMTYPE',
                        'ENOKEY',
                        'ENOMEDIUM',
                        'ENOTRECOVERABLE',
                        'EOWNERDEAD',
                        'ERFKILL'
                     ]

   def from_code(self, code):
      num = code -1 # index correction
      print('{}: {}'.format(code, self.err_str[num]))
      print(' - {}'.format(os.strerror(code)))

   def from_string(self, input_string):
      counter = 1 # 0 could be used, but aligning value with command line number input
      for e in (self.err_str):
         if e == input_string:
            self.from_code(counter)
            break

         counter += 1

   def display_all(self):
      counter = 1 # as above
      for e in (self.err_str):
         self.from_code(counter)
         counter += 1


if __name__ == "__main__":

   arg_parser = argparse.ArgumentParser(description='Errno Converter - Convert regular errno codes to a human readable description')

   arg_parser.add_argument('--code', action='store', help= 'The error code to convert', required=False)
   arg_parser.add_argument('--string', action='store', help= 'The error string description to convert', required=False)
   arg_parser.add_argument('--display', action='store_true', default=False, help= 'Display all error code description', required=False)

   # Get the input arguments
   args = arg_parser.parse_args()

   error_handler = ErrorHndlr()
   if args.code is not None:
      error_handler.from_code(int(args.code))
      exit()

   if args.string is not None:
      error_handler.from_string(str(args.string))
      exit()

   if args.display == True:
      error_handler.display_all()
      exit()

# Complete list for debugging
#for i in sorted(errno.errorcode) :
#   print('#{}: {}'.format(i, os.strerror(i)))


