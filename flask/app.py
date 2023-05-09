from flask import Flask,render_template

app=Flask('pozdravy')

@app.route('/factorial')
def factorial():

    fact=[]
    n=1
    for i in range(1,10):
        n=n*i
        fact.append((i,n))
    return render_template('tabulate.html',data=fact,function="faktoriál")

@app.route('/hello/<who>')
def hello_somebody(who):
    return f'<html><body><h1>Hello {who}!</h1></body></html>'
    
