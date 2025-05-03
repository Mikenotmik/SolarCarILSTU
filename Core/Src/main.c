/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "can.h"
#include "dma.h"
#include "fatfs.h"
#include "rtc.h"
#include "spi.h"
#include "usb_device.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */


/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_CAN_Init();
  MX_SPI1_Init();
  MX_FATFS_Init();
  MX_USB_DEVICE_Init();
  MX_RTC_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */
  /* USER CODE BEGIN 2 */
  uint32_t adc_val = 0;
  float potPercent = 0.0f;
  float alpha = 0.0f;
  float omega = 0.0f;
  static GPIO_PinState last_gear_state = GPIO_PIN_SET;  // assume default is high

  CAN_TxHeaderTypeDef TxHeader;
  uint8_t can_data[8];
  uint32_t TxMailbox;

  TxHeader.StdId = 0x501;
  TxHeader.IDE = CAN_ID_STD;
  TxHeader.RTR = CAN_RTR_DATA;
  TxHeader.DLC = 8;  // 2 floats = 8 bytes

  HAL_CAN_Start(&hcan);
  HAL_CAN_ActivateNotification(&hcan, CAN_IT_TX_MAILBOX_EMPTY);

  /* USER CODE END 2 */


  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
      // === 1. Read pedal analog value ===
      HAL_ADC_Start(&hadc1);
      HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
      adc_val = HAL_ADC_GetValue(&hadc1);
      HAL_ADC_Stop(&hadc1);

      potPercent = (float)adc_val / 4095.0f;
      if (potPercent < 0.05f) potPercent = 0.0f;

      // === 2. Apply thrust model ===
      alpha = powf(potPercent, 1.75f) * 0.9f;
      if (alpha < 0.01f) alpha = 0.0f;

      // === 3. Read digital GPIOs ===
      GPIO_PinState forward = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_5);  // change pin as needed
      GPIO_PinState reverse = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_6);
      GPIO_PinState regen   = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_7);

      // === Detect gear select state ===
      /*static uint32_t last_shift_time = 0;
      uint32_t now = HAL_GetTick();  // ms

      if ((gear_select != last_gear_state) && (now - last_shift_time > 500)) {
          last_shift_time = now;
          // then perform gear change...
      }*/

      GPIO_PinState gear_select = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_9);

      if (gear_select != last_gear_state) {
          // === Gear select changed! ===

          // 1. Set alpha and omega to zero
          alpha = 0.0f;
          omega = 0.0f;

          // 2. Send zero-thrust CAN message
          memcpy(&can_data[0], &omega, 4);
          memcpy(&can_data[4], &alpha, 4);
          HAL_CAN_AddTxMessage(&hcan, &TxHeader, can_data, &TxMailbox);

          HAL_Delay(100);  // short delay to allow motor controller to receive

          // 3. Change gear outputs based on new state
          if (gear_select == GPIO_PIN_SET) {
              // Normal state: Gear 1 high, Gear 2 low
              HAL_GPIO_WritePin(GPIOA, GPIO_PIN_10, GPIO_PIN_SET);   // Gear 1 ON
              HAL_GPIO_WritePin(GPIOA, GPIO_PIN_11, GPIO_PIN_RESET); // Gear 2 OFF
          } else {
              // Select state: Gear 1 low, Gear 2 high
              HAL_GPIO_WritePin(GPIOA, GPIO_PIN_10, GPIO_PIN_RESET); // Gear 1 OFF
              HAL_GPIO_WritePin(GPIOA, GPIO_PIN_11, GPIO_PIN_SET);   // Gear 2 ON
          }

          // 4. Update last state
          last_gear_state = gear_select;
      }



      // === 4. Compute omega ===
      if (reverse == GPIO_PIN_RESET) {
          omega = -1000.0f;
      } else if (forward == GPIO_PIN_RESET) {
          omega = 1000.0f;
      } else {
          omega = 0.0f;
      }

      if (regen == GPIO_PIN_RESET) {
          alpha *= 0.4f;
          omega = 0.0f;
      }

      // === 5. Pack and send CAN message ===
      memcpy(&can_data[0], &omega, 4);
      memcpy(&can_data[4], &alpha, 4);
      HAL_CAN_AddTxMessage(&hcan, &TxHeader, can_data, &TxMailbox);

      HAL_Delay(100);
  }
  /* USER CODE END WHILE */


}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE|RCC_OSCILLATORTYPE_LSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.LSEState = RCC_LSE_ON;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC|RCC_PERIPHCLK_ADC
                              |RCC_PERIPHCLK_USB;
  PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV6;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
