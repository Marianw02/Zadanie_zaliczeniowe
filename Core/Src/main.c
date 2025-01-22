/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
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
#include "eth.h"
#include "spi.h"
#include "tim.h"
#include "usart.h"
#include "usb_otg.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "bmp2_config.h"
#include <stdlib.h>
#include <stdio.h>
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
double temp = 0.0f, press = 0.0f;
uint32_t tx_buffer[128], rx_buffer[30];
unsigned int tx_msg_len, rx_msg_len = 1, press_calk, temp_calk;
int temp_zadana = 0, wartosc_odebrana;
_Bool grzanie = 0, chlodzenie = 0;
uint16_t odebrane_znaki = 0, prosba_temp = 0, war_max = 84, war_min = 12;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    HAL_UART_Receive_IT(&huart3, rx_buffer, rx_msg_len);
	if(sizeof(strtol((char*)&rx_buffer[0], 0, 10)) == 4)//jesli to int
		wartosc_odebrana = strtol((char*)&rx_buffer[0], 0, 10);

	prosba_temp = prosba_temp * 10 + wartosc_odebrana;

	if (huart->Instance == USART3) {  // Jeśli UART odebrał znak
		odebrane_znaki++;
	}

	if(odebrane_znaki == 2){
		odebrane_znaki = 0;
		if(prosba_temp >= war_min && prosba_temp <= war_max){
			temp_zadana = prosba_temp;
		}
		prosba_temp = 0;
	}
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	if (GPIO_Pin == Btn_up_Pin){
		if(temp_zadana <= war_max){
			temp_zadana += 1;
		}
	}
	if (GPIO_Pin == Btn_down_Pin){
		if(temp_zadana >= war_min){
			temp_zadana -= 1;
		}
	}
}

void grzanie_f(int temp_zadana)
{
	HAL_GPIO_WritePin(przek_grzalka_GPIO_Port, przek_grzalka_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(przek_wiatrak_GPIO_Port, przek_wiatrak_Pin, GPIO_PIN_RESET);
}
void chlodzenie_f(int temp_zadana)
{
	HAL_GPIO_WritePin(przek_wiatrak_GPIO_Port, przek_wiatrak_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(przek_grzalka_GPIO_Port, przek_grzalka_Pin, GPIO_PIN_RESET);
}
void oczekiwanie_f(int temp_zadana)
{
	HAL_GPIO_WritePin(przek_wiatrak_GPIO_Port, przek_wiatrak_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(przek_grzalka_GPIO_Port, przek_grzalka_Pin, GPIO_PIN_SET);
}

void odbieranie_usart_f()
{
	BMP2_ReadData(&bmp2dev, &press, &temp);
	press_calk = 1000.0f * press / 1000;
	temp_calk = 1000.0f * temp / 1000;

	HAL_UART_Receive_IT(&huart3, rx_buffer, rx_msg_len);
	if(wartosc_odebrana >= war_min && wartosc_odebrana <= war_max)
		temp_zadana = wartosc_odebrana;
}

void sterowanie_f()
{
	if (!grzanie && temp_calk < (temp_zadana)) {
		grzanie = 1;
	    chlodzenie = 0;
	    grzanie_f(temp_zadana);
	}
	else if (grzanie && !chlodzenie && temp_calk > (temp_zadana - 1)) {
		grzanie = 0;
		oczekiwanie_f(temp_zadana);
	}

	if (!chlodzenie && temp_calk > temp_zadana) {
		chlodzenie = 1;
		grzanie = 0;
		chlodzenie_f(temp_zadana);
	}else if (chlodzenie && !grzanie && temp_calk < temp_zadana) {
		chlodzenie = 0;
		oczekiwanie_f(temp_zadana);
	}
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if(htim == &htim4){
	  odbieranie_usart_f();
	  sterowanie_f();
  }
}
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
  MX_ETH_Init();
  MX_USART3_UART_Init();
  MX_USB_OTG_FS_PCD_Init();
  MX_SPI4_Init();
  MX_TIM4_Init();
  /* USER CODE BEGIN 2 */
  BMP2_Init(&bmp2dev);
  MX_TIM4_Init();
  HAL_UART_Receive_IT(&huart3, tx_buffer, tx_msg_len);
  HAL_TIM_Base_Start_IT(&htim4);

  HAL_GPIO_WritePin(przek_grzalka_GPIO_Port, przek_grzalka_Pin, GPIO_PIN_SET);
  HAL_GPIO_WritePin(przek_wiatrak_GPIO_Port, przek_wiatrak_Pin, GPIO_PIN_SET);

  BMP2_ReadData(&bmp2dev, &press, &temp);
  HAL_Delay(10);
  BMP2_ReadData(&bmp2dev, &press, &temp);
  temp_zadana = 1000.0f * temp / 1000;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  tx_msg_len = sprintf((char*)tx_buffer, "Aktualna temperatura: %2u C, ustawiona temperatura: %2u C. Ustaw wybrana wartosc temperatury:\r", temp_calk, temp_zadana);
	  HAL_UART_Transmit(&huart3, tx_buffer, tx_msg_len, 100);
	  odebrane_znaki = 0;
	  prosba_temp = 0;

	  HAL_Delay(500);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure LSE Drive Capability
  */
  HAL_PWR_EnableBkUpAccess();

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_BYPASS;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 72;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 3;
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
