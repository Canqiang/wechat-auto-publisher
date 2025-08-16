#!/bin/bash
echo "🛑 停止开发服务..."
pkill -f "python app.py"
pkill -f "npm start"
echo "✅ 所有服务已停止"
