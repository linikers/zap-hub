#!/usr/bin/env bash
# Starts the WhatsApp bridge and generates a QR code image
cd /usr/local/lib/hermes-agent/scripts/whatsapp-bridge

# Kill any existing bridge
pkill -f "bridge.js" 2>/dev/null
sleep 1

# Start the bridge and capture output
node bridge.js --port 3000 --session /root/.hermes/whatsapp/session --mode self-chat 2>&1 | tee /tmp/whatsapp-bridge.log &

BRIDGE_PID=$!
echo "Bridge PID: $BRIDGE_PID"
echo "Waiting for QR code..."

# Wait for QR code in output
for i in $(seq 1 30); do
    if grep -q "Scan this QR code" /tmp/whatsapp-bridge.log 2>/dev/null; then
        echo "QR code found!"
        break
    fi
    sleep 1
done

# Generate QR code image from the bridge - use Node.js to re-output the QR
# as a data URL we can capture
echo ""
echo "=== SCAN THIS QR CODE WITH YOUR WHATSAPP ==="
echo ""
echo "1. Open WhatsApp on your phone"
echo "2. Go to Settings → Linked Devices → Link a Device"
echo "3. Scan the QR code above"
echo ""

wait $BRIDGE_PID
