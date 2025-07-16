# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

# 初始化 Flask 应用
app = Flask(__name__)

def analyze_strategy(
    deposit_days: int,
    funding_rate: float,
    spot_interest_apy: float,
    spot_fee: float,
    contract_fee: float,
    rebate_ratio: float,
    leverage: int,
    funding_interval_hours: int
) -> tuple[float, float]:
    """这是我们之前写的核心计算函数，保持不变"""
    principal_spot = 1.0
    net_fee_cost = (principal_spot * spot_fee * 2 + principal_spot * contract_fee * 2) * (1 - rebate_ratio)
    
    settlements_per_day = 24 / funding_interval_hours
    daily_funding_income = principal_spot * funding_rate * settlements_per_day
    daily_spot_interest_income = principal_spot * spot_interest_apy / 365
    total_daily_income = daily_funding_income + daily_spot_interest_income

    if total_daily_income > 0:
        break_even_days = net_fee_cost / total_daily_income
    else:
        break_even_days = float('inf')

    total_profit = (total_daily_income * deposit_days) - net_fee_cost
    principal_contract_margin = principal_spot / leverage
    total_principal = principal_spot + principal_contract_margin
    period_return_rate = total_profit / total_principal

    if deposit_days > 0:
        apy = period_return_rate * (365 / deposit_days)
    else:
        apy = 0
        
    return apy, break_even_days

# 创建网站的路由（访问地址）
@app.route('/', methods=['GET', 'POST'])
def index():
    # 设定默认值
    defaults = {
        'deposit_days': 90,
        'funding_rate': 0.0001,
        'spot_interest_apy': 0.0,
        'spot_fee': 0.001,
        'contract_fee': 0.00055,
        'rebate_ratio': 0.33,
        'leverage': 1,
        'funding_interval_hours': 8
    }
    
    # 如果用户提交了表单 (POST请求)
    if request.method == 'POST':
        try:
            # 从网页表单中获取用户输入的值，并转换为正确的数字类型
            days = request.form.get('deposit_days', type=int)
            funding_r = request.form.get('funding_rate', type=float)
            spot_apy = request.form.get('spot_interest_apy', type=float)
            spot_f = request.form.get('spot_fee', type=float)
            contract_f = request.form.get('contract_fee', type=float)
            rebate_r = request.form.get('rebate_ratio', type=float)
            lev = request.form.get('leverage', type=int)
            interval = request.form.get('funding_interval_hours', type=int)

            # 调用函数进行计算
            apy_result, breakeven_days_result = analyze_strategy(
                deposit_days=days,
                funding_rate=funding_r,
                spot_interest_apy=spot_apy,
                spot_fee=spot_f,
                contract_fee=contract_f,
                rebate_ratio=rebate_r,
                leverage=lev,
                funding_interval_hours=interval
            )

            # 将计算结果和用户输入一起传回给页面进行显示
            return render_template('index.html', results={
                'apy': apy_result,
                'breakeven': breakeven_days_result
            }, user_input=request.form)

        except Exception as e:
            # 如果出现错误，返回一个错误信息
            return render_template('index.html', error=f"计算出错，请检查输入值。错误: {e}", user_input=defaults)
            
    # 如果是第一次打开页面 (GET请求)，就只显示一个带默认值的空表单
    return render_template('index.html', user_input=defaults)

if __name__ == '__main__':
    # 这行只在本地测试时运行，部署时不会用到
    app.run(debug=True)