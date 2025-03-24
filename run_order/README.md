# deep-for-binary-pred-forex
Time Series Forecasting with Ensemble Learning and Stacked Recurrent Networks for forex Candlestick pred

**Description:**

This repository implements a time series forecasting model to predict the direction (up or down) of the next 5-minute Candlestick for a given instrument. The model leverages ensemble learning techniques, specifically stacking, to combine the strengths of multiple recurrent neural networks.

**Key Features:**

*   **Ensemble Learning:** Employs ensemble methods to improve prediction accuracy and robustness.
*   **Stacking:** Uses a final LSTM layer to combine the outputs of two base models (LSTM and CNN-LSTM).
*   **Recurrent Neural Networks:** Utilizes LSTM and CNN-LSTM architectures to capture temporal dependencies in the time series data.
*   **Candlestick Prediction:** Designed to predict the upward or downward movement of the next 5-minute candlestick.

**How It Works:**

1.  Two base models, LSTM and CNN-LSTM, are trained on historical time series data.
2.  The predictions from these base models are then fed into a final LSTM layer.
3.  This final LSTM layer learns to combine the predictions of the base models, producing the final forecast for the direction of the next candlestick.

**Potential Use Cases:**

*   Algorithmic trading
*   Financial forecasting
*   Market analysis



