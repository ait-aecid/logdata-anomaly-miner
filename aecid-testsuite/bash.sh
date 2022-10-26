for x in {0..100} ; do
    if (( x % 1 == 0 ))
    then
        sudo bash runAminerIntegrationTest.sh aminerIntegrationTest2.sh config21.py config22.py
    fi
    sleep 1
done
