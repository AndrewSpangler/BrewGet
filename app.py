from src import app

if __name__ == "__main__":
    # CERTS = (
    #     f'certs/####.crt',
    #     f'certs/####.-decrypted.key',
    # )
    app.run(
        host="0.0.0.0",
        port=443,
        # ssl_context=CERTS,
        threaded=True
    )
    # app.run(host="0.0.0.0", port=80, threaded=True)