#!/bin/bash
#
# Parses DHCP options from openvpn to update resolv.conf
# To use set as 'up' and 'down' script in your openvpn *.conf:
# up /etc/openvpn/update-resolv-conf
# down /etc/openvpn/update-resolv-conf
#
# Used snippets of resolvconf script by Thomas Hood <jdthood@yahoo.co.uk>
# and Chris Hanson
# Licensed under the GNU GPL.  See /usr/share/common-licenses/GPL.
# 07/2013 colin@daedrum.net Fixed intet name
# 05/2006 chlauber@bnc.ch
#
# Example envs set from openvpn:
# foreign_option_1='dhcp-option DNS 193.43.27.132'
# foreign_option_2='dhcp-option DNS 193.43.27.133'
# foreign_option_3='dhcp-option DOMAIN be.bnc.ch'

# @param String message - The message to log
logMessage()
{
        echo "${@}"
}

##########################################################################################
flushDNSCache()
{
    if ${ARG_FLUSH_DNS_CACHE} ; then
            if [ "${OSVER}" = "10.4" ] ; then

                        if [ -f /usr/sbin/lookupd ] ; then
                                set +e # we will catch errors from lookupd
                                /usr/sbin/lookupd -flushcache
                                if [ $? != 0 ] ; then
                                        logMessage "WARNING: Unable to flush the DNS cache via lookupd"
                                else
                                        logMessage "Flushed the DNS cache via lookupd"
                                fi
                                set -e # bash should again fail on errors
                        else
                                logMessage "WARNING: /usr/sbin/lookupd not present. Not flushing the DNS cache"
                        fi

                else

                        if [ -f /usr/bin/dscacheutil ] ; then
                                set +e # we will catch errors from dscacheutil
                                /usr/bin/dscacheutil -flushcache
                                if [ $? != 0 ] ; then
                                        logMessage "WARNING: Unable to flush the DNS cache via dscacheutil"
                                else
                                        logMessage "Flushed the DNS cache via dscacheutil"
                                fi
                                set -e # bash should again fail on errors
                        else
                                logMessage "WARNING: /usr/bin/dscacheutil not present. Not flushing the DNS cache via dscacheutil"
                        fi

			if [ -f /usr/sbin/discoveryutil ] ; then
                                set +e # we will catch errors from discoveryutil
                                /usr/sbin/discoveryutil udnsflushcaches
                                if [ $? != 0 ] ; then
                                        logMessage "WARNING: Unable to flush the DNS cache via discoveryutil udnsflushcaches"
                                else
                                        logMessage "Flushed the DNS cache via discoveryutil udnsflushcaches"
                                fi
                                /usr/sbin/discoveryutil mdnsflushcache
                                if [ $? != 0 ] ; then
                                        logMessage "WARNING: Unable to flush the DNS cache via discoveryutil mdnsflushcache"
                                else
                                        logMessage "Flushed the DNS cache via discoveryutil mdnsflushcache"
                                fi
                                set -e # bash should again fail on errors
                        else
                                logMessage "/usr/sbin/discoveryutil not present. Not flushing the DNS cache via discoveryutil"
                        fi

                        set +e # "grep" will return error status (1) if no matches are found, so don't fail on individual errors
                        hands_off_ps="$( ps -ax | grep HandsOffDaemon | grep -v grep.HandsOffDaemon )"
                        set -e # We instruct bash that it CAN again fail on errors
                        if [ "${hands_off_ps}" = "" ] ; then
                                if [ -f /usr/bin/killall ] ; then
                                        set +e # ignore errors if mDNSResponder isn't currently running
                                        /usr/bin/killall -HUP mDNSResponder
                                        if [ $? != 0 ] ; then
                                                logMessage "mDNSResponder not running. Not notifying it that the DNS cache was flushed"
                                        else
                                                logMessage "Notified mDNSResponder that the DNS cache was flushed"
                                        fi
                                        set -e # bash should again fail on errors
                                else
                                        logMessage "WARNING: /usr/bin/killall not present. Not notifying mDNSResponder that the DNS cache was flushed"
                                fi
                        else
                                logMessage "WARNING: Hands Off is running.  Not notifying mDNSResponder that the DNS cache was flushed"
                        fi

                fi
    fi
}




##########################################################################################
#
# START OF SCRIPT
#
##########################################################################################

export PATH="/bin:/sbin:/usr/sbin:/usr/bin"

readonly OUR_NAME="$( basename "${0}" )"

logMessage "**********************************************"
logMessage "Start of output from ${OUR_NAME}"

publicDNS="114.114.114.114"

case $script_type in

up)
   for optionname in ${!foreign_option_*} ; do
      option="${!optionname}"
      echo $option
      part1=$(echo "$option" | cut -d " " -f 1)
      if [ "$part1" == "dhcp-option" ] ; then
         part2=$(echo "$option" | cut -d " " -f 2)
         part3=$(echo "$option" | cut -d " " -f 3)
         if [ "$part2" == "DNS" ] ; then
            IF_DNS_NAMESERVERS="$IF_DNS_NAMESERVERS $part3"
         fi
         if [ "$part2" == "DOMAIN" ] ; then
            IF_DNS_SEARCH="$IF_DNS_SEARCH $part3"
         fi
      fi
   done
   R=""
   if [ "$IF_DNS_SEARCH" ] ; then
           R="${R}search $IF_DNS_SEARCH"
   fi
   for NS in $IF_DNS_NAMESERVERS ; do
           R="${R}nameserver $NS"
   done
   #echo -n "$R" | resolvconf -p -a "${dev}"
   #echo -n "$R" | /usr/bin/resolvconf -a "${dev}.inet"
   /usr/sbin/networksetup -setdnsservers Ethernet $IF_DNS_NAMESERVERS $publicDNS
   /usr/sbin/networksetup -setdnsservers Wi-Fi $IF_DNS_NAMESERVERS $publicDNS
   logMessage "WARNING: dns for Ethernet / WiFi was set to $IF_DNS_NAMESERVERS $publicDNS"
   flushDNSCache
   ;;

down)
   /usr/sbin/networksetup -setdnsservers Ethernet  $publicDNS
   /usr/sbin/networksetup -setdnsservers Wi-Fi $publicDNS
   logMessage "WARNING: dns for Ethernet / WiFi was set to $publicDNS"
   flushDNSCache
   ;;
esac

logMessage "End of output from ${OUR_NAME}"
logMessage "******************************************"

exit 0
#/usr/sbin/networksetup -setdnsservers Ethernet 172.17.0.1 114.114.114.114
