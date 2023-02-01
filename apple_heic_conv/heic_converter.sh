#!/bin/bash

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Filename: install.sh
# File Description: Converts Apple .HEIC files (pics) to .jpg instead.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -¬

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Variables¬
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LOG_TAG="[heic_converter] -"
SCRIPT_VERSION="1.0.0"
HEIC_SUFFIX=".HEIC"
DIRECTORY_PATH=""
FILE_NAME=""
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flags¬
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
VERBOSE_LOGGING=false

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Support functions¬
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

usage() {
   cat <<EOF
Description:
Script for converting Apple .HEIC files to .jpg.

Usage: [hvdfV]
-v   Enable verbose logging
-d   Convert all .HEIC files within specified directory
-f   Specify single .HEIC file to convert
-h   Print this help
-V   Print script version

EOF
}

log_verbose() {
   if [ "${VERBOSE_LOGGING}" = true ]; then
      log "$1"
   fi
}

log() {
   echo "${LOG_TAG} $1"
}


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main functionality¬
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

verify_required_tools() {
   log_verbose "Verifying needed convert tool"

   local heif_convert_tool=`which heif-convert`
   if [ -z "${heif_convert_tool}" ]; then
      log "Unable to find heif-convert, can be installed with: apt install libheif-examples"
      exit 1
   fi

   log_verbose "heif-convert found"
}

convert_heic_to_jpg() {
   local file_name=$1
   log_verbose "Converting ${file_name}"

   heif-convert -q 100 ${file_name} ${file_name%.HEIC}.jpg

   if [ $? -ne 0 ]; then
      log "Failed to convert file: ${file_name} with following details:"
      file "${file_name}"
   else
      log_verbose "Done"
   fi

   # Basic loop from : https://ubuntuhandbook.org/index.php/2021/06/open-heic-convert-jpg-png-ubuntu-20-04/
   #for file in *.HEIC; do heif-convert -q 100 $file ${file%.HEIC}.jpg; done
}

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

while getopts 'hvVd:f:' OPT; do
   case $OPT in
      d)
         DIRECTORY_PATH="${OPTARG}"
         ;;

      f)
         FILE_NAME="${OPTARG}"
         ;;

      h)
         usage
         exit 0
         ;;

      v)
         VERBOSE_LOGGING=true
         ;;

      V)
         echo "$0 - version: $SCRIPT_VERSION"
         exit 0
         ;;

      \?)
         usage
         exit 0
         ;;

      *)
         usage
         exit 0
         ;;
   esac
done
shift $((OPTIND-1))

echo "test print: file name = ${FILE_NAME}, DIRECTORY_PATH= ${DIRECTORY_PATH}"
verify_required_tools

# Verify directory input, if existing convert all files
if [ ! -z "${DIRECTORY_PATH}" ]; then

   if [ ! -d "${DIRECTORY_PATH}" ]; then
      log "Unable to find directory with name: ${DIRECTORY_PATH}"
      exit 1
   fi

   heic_files="${DIRECTORY_PATH}/*${HEIC_SUFFIX}"
   log_verbose "Converting ${HEIC_SUFFIX} files in: ${DIRECTORY_PATH}"

   for file in ${heic_files}; do
      # Debug prints if needed
      #echo "${heic_files}"
      #echo "${file}"
      convert_heic_to_jpg $file
   done
   log "Converted all available ${HEIC_SUFFIX} files in: ${DIRECTORY_PATH}"

# Verify file input, if existing convert file
elif [ ! -z "${FILE_NAME}" ]; then

   if [ ! -f "${FILE_NAME}" ]; then
      log "Unable to find file with name: ${FILE_NAME}"
      exit 1
   fi

   convert_heic_to_jpg "${FILE_NAME}"

else
   log "No INPUT argument provided, see $0 -h for usage"
fi

exit 0

