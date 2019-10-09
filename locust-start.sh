case ${LOCUST_TYPE} in
    master)
        locust --master --host=${HOST_TO_TEST}
	;;
    slave)
	locust --slave --master-host=${HOST_MASTER} --host=${HOST_TO_TEST}
        ;;
esac
