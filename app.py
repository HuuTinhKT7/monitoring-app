import psutil
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Định nghĩa Counter với nhãn
http_requests_total = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'status'])

# Định nghĩa Histogram với nhãn trực tiếp từ prometheus_client
request_latency = Histogram('request_latency_seconds', 'Request Latency', ['method'])

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Cập nhật số liệu
    http_requests_total.labels(method=request.method, status=response.status_code).inc()
    latency = time.time() - request.start_time
    request_latency.labels(method=request.method).observe(latency)
    return response

@app.route("/")
def index():
    cpu_metric = psutil.cpu_percent()
    mem_metric = psutil.virtual_memory().percent
    message = None
    if cpu_metric > 80 or mem_metric > 80:
        message = "High CPU or Memory Detected, scale up!!!"
    return render_template("index.html", cpu_metric=cpu_metric, mem_metric=mem_metric, message=message)

@app.route('/metrics')
def metrics_endpoint():
    from flask import Response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

