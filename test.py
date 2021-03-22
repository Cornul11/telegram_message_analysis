from progress.bar import Bar
import time

bar = Bar('Processing', max=100)
for i in range(100):
    bar.next()
    time.sleep(0.5)
bar.finish()
