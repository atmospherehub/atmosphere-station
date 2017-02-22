#!/bin/sh

### BEGIN INIT INFO
# Provides:          atmosphere-station
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Atmosphere station service client
# Description:       Detects faces from video stream and send them to HTTP endpoint
### END INIT INFO

DIR=/home/pi/atmosphere-station
DAEMON=$DIR/__main__.py
DAEMON_NAME=atmosphere-station

# determines what user the script runs as
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

# pass gateway configurations to clien
. /etc/environment
DAEMON_OPTS="-e $ATMOSPHERE_ENDPOINT -d true"

# currently the ugly but working way to update the client on start
update_client() {
    cd $DIR 
    {
        git reset --hard > /dev/null
        git pull -f > /dev/null 
        chmod 755 $DAEMON 
        log_progress_msg ":)"
    } ||
    {
        log_progress_msg ":("
    }
    cd - > /dev/null
}

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    update_client
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
    log_progress_msg "done"
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0