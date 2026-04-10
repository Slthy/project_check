from create_instance import instance

app = instance()

if __name__ == '__main__':
    app.run(debug=True)