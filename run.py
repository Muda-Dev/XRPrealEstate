from helpers.config import version
import sys
from helpers.dbhelper import Database as Db
from waitress import serve
import os
from controllers.account import bp_app as account
from flask import Flask
from application import application
import asyncio
from pickle import FALSE
from application.XRPCronService import main
from dotenv import load_dotenv

load_dotenv()
application.register_blueprint(account)

print("starting realState")
print("version", version)

if os.getenv("callback_url") == "":
    print("callback url needs to be set")
    exit()

try:
    arg_1 = "provider"
    arg_2 = "client"
    arg_count = 0

    if sys.argv:
        arg_count = len(sys.argv)
        print(arg_count)

    if arg_count > 1:
        arg_1 = sys.argv[1]

    with application.app_context():
        response = Db().checkConnection()
        if response == FALSE:
            print("Database connection error. exiting ...")
            exit()

    if arg_1 == "db-migrate":
        print("starting db migrations")
        with application.app_context():
            Db().migrate_db()
            exit()

    if arg_1 != "provider":
        print("arg one should be 'provider'")
        exit()

    if arg_count > 2:
        arg_2 = sys.argv[2]

    if arg_2 == "service":
        print("starting service in provider mode")
        print("Initiating the XRP Ingestion Service")
        asyncio.run(main())

    elif arg_2 == "client":
        print("starting service in client mode")
        print("app started on port " + os.environ.get("PORT"))
        if os.getenv("mode") == "dev":
            application.run(port=os.environ.get("PORT"), host="0.0.0.0", debug=True)
        else:
            serve(application, host="0.0.0.0", port=os.environ.get("PORT"))

    else:
        print("unexpected arg..")
        exit()

except Exception as e:
    print("an exception was thrown, make sure you have the correct arguments")
    print(e)
    exit()
