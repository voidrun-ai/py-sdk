import time
import sys
from voidrun import VoidRun

def main():
    vr = VoidRun()

    print('Creating sandbox for large code tests...')
    create_resp = vr.sandboxes.create(name='test-large-code-py')
    sandbox = create_resp.data

    try:
        print('\n--- Testing Complex JavaScript Code (>1000 chars) ---')
        print('Scenario: Stock Market Simulation with Volatility')
        
        large_js = """
/**
 * Simulated Stock Market Engine
 * This script simulates the price movements of multiple stocks over a period of time
 * using a simplified random walk with volatility.
 */

class Stock {
    constructor(ticker, price) {
        this.ticker = ticker;
        this.price = price;
        this.history = [price];
    }

    update() {
        // Daily price movement: random float between -2.5% and +2.5%
        const change = 1 + (Math.random() * 0.05 - 0.025);
        this.price = Math.round((this.price * change) * 100) / 100;
        this.history.push(this.price);
    }
}

function runSimulation(days) {
    const portfolio = [
        new Stock("TECH", 150.00),
        new Stock("ENRG", 45.30),
        new Stock("RETL", 88.10),
        new Stock("HLTH", 120.50)
    ];

    console.log("--- Starting 30-Day Market Simulation ---");
    for (let day = 1; day <= days; day++) {
        portfolio.forEach(stock => stock.update());
    }

    console.log("Simulation Complete. Results:");
    portfolio.forEach(stock => {
        const start = stock.history[0];
        const end = stock.price;
        const diff = (end - start).toFixed(2);
        const pct = (((end / start) - 1) * 100).toFixed(2);
        console.log(`  ${stock.ticker}: ${start} -> ${end} (${diff} / ${pct}%)`);
    });

    return portfolio.length;
}

console.log(runSimulation(30));
"""

        print(f"JS Code length: {len(large_js)} characters")
        result = sandbox.run_code(large_js, language='javascript')
        exec_result = result.data
        print('Stdout output:\n', exec_result.stdout.strip())
        
        if "30-Day Market Simulation" in exec_result.stdout and exec_result.results == 4:
            print("✅ Complex JS execution PASS")
        else:
            print("❌ Complex JS execution FAIL")
            sys.exit(1)

        print('\n--- Testing Complex Python Code (>1000 chars) ---')
        print('Scenario: Climate Data Statistical Analysis')

        large_py = """
\"\"\"
Climate Data Analysis Tool
This script simulates processing a large set of daily temperature readings
and calculates statistical metrics including moving averages and anomalies.
\"\"\"

import random

def generate_sensor_data(days=365):
    # Base temp 15C, with annual seasonality and random noise
    data = []
    for day in range(days):
        seasonality = 10 * (day % 365 / 365) # Simple linear ramp for complexity
        noise = random.uniform(-2, 2)
        data.append(round(15 + seasonality + noise, 2))
    return data

def analyze_temperatures(data):
    count = len(data)
    avg = sum(data) / count
    max_t = max(data)
    min_t = min(data)
    
    # Calculate 7-day moving average
    moving_avgs = []
    for i in range(len(data)):
        if i < 7:
            moving_avgs.append(None)
        else:
            window = data[i-7:i]
            moving_avgs.append(round(sum(window) / 7, 2))
            
    print(f"--- Processed {count} Days of Climate Data ---")
    print(f"Global Average: {avg:.2f} C")
    print(f"Peak recorded: {max_t} C")
    print(f"Minimum recorded: {min_t} C")
    print(f"First 5 Moving Averages: {moving_avgs[7:12]}")
    
    return count

print(analyze_temperatures(generate_sensor_data(500)))
"""

        print(f"Python Code length: {len(large_py)} characters")
        result = sandbox.run_code(large_py, language='python')
        exec_result = result.data
        print('Stdout output:\n', exec_result.stdout.strip())

        if "Processed 500 Days" in exec_result.stdout and exec_result.results == 500:
            print("✅ Complex Python execution PASS")
        else:
            print("❌ Complex Python execution FAIL")
            sys.exit(1)

    except Exception as e:
        print(f'Test execution failed: {e}')
        sys.exit(1)
    finally:
        print('\nRemoving sandbox...')
        sandbox.delete()
        print('Done.')

if __name__ == "__main__":
    main()
