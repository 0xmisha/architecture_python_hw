workspace "Система бронирования отелей" "Архитектура системы бронирования отелей (вариант 13)" {

    model {
        guest = person "Гость" "Пользователь, который ищет и бронирует отели"
        hotelManager = person "Менеджер отеля" "Управляет информацией об отелях и просматривает бронирования"
        admin = person "Администратор" "Администрирует систему"

        paymentSystem = softwareSystem "Платежная система" "Обрабатывает платежи за бронирования (Stripe, PayPal)"
        emailSystem = softwareSystem "Email сервис" "Отправляет email уведомления пользователям"
        smsSystem = softwareSystem "SMS сервис" "Отправляет SMS уведомления"
        mapsService = softwareSystem "Сервис карт" "Предоставляет информацию о местоположении отелей (Google Maps)"

        bookingSystem = softwareSystem "Система бронирования отелей" "Позволяет пользователям искать и бронировать отели" {

            webApp = container "Web Application" "Предоставляет функциональность бронирования через веб-браузер" "React, TypeScript" "WebBrowser"
            mobileApp = container "Mobile Application" "Предоставляет функциональность бронирования через мобильное приложение" "React Native" "Mobile"

            apiGateway = container "API Gateway" "Точка входа для всех API запросов, маршрутизация и аутентификация" "Kong, Nginx" "API"

            userService = container "User Service" "Управление пользователями: регистрация, аутентификация, профили" "Python, FastAPI" "Service"
            hotelService = container "Hotel Service" "Управление информацией об отелях, поиск отелей" "Python, FastAPI" "Service"
            bookingService = container "Booking Service" "Управление бронированиями: создание, отмена, получение списка" "Python, FastAPI" "Service"
            notificationService = container "Notification Service" "Отправка уведомлений пользователям" "Python, FastAPI" "Service"
            paymentService = container "Payment Service" "Обработка платежей и взаимодействие с платежными системами" "Python, FastAPI" "Service"

            userDB = container "User Database" "Хранит информацию о пользователях" "PostgreSQL" "Database"
            hotelDB = container "Hotel Database" "Хранит информацию об отелях" "PostgreSQL" "Database"
            bookingDB = container "Booking Database" "Хранит информацию о бронированиях" "PostgreSQL" "Database"

            cache = container "Cache" "Кэширует часто запрашиваемые данные" "Redis" "Cache"
            messageQueue = container "Message Queue" "Асинхронная обработка событий" "RabbitMQ" "Queue"

            guest -> webApp "Ищет и бронирует отели через" "HTTPS"
            guest -> mobileApp "Ищет и бронирует отели через" "HTTPS"
            hotelManager -> webApp "Управляет отелями через" "HTTPS"
            admin -> webApp "Администрирует систему через" "HTTPS"

            webApp -> apiGateway "Отправляет API запросы" "HTTPS/REST"
            mobileApp -> apiGateway "Отправляет API запросы" "HTTPS/REST"

            apiGateway -> userService "Маршрутизирует запросы пользователей" "HTTPS/REST"
            apiGateway -> hotelService "Маршрутизирует запросы по отелям" "HTTPS/REST"
            apiGateway -> bookingService "Маршрутизирует запросы по бронированиям" "HTTPS/REST"

            userService -> userDB "Читает/записывает данные пользователей" "JDBC/SQL"
            hotelService -> hotelDB "Читает/записывает данные об отелях" "JDBC/SQL"
            bookingService -> bookingDB "Читает/записывает данные о бронированиях" "JDBC/SQL"

            hotelService -> cache "Кэширует результаты поиска" "Redis Protocol"
            userService -> cache "Кэширует сессии пользователей" "Redis Protocol"

            bookingService -> hotelService "Проверяет доступность номеров" "HTTPS/REST"
            bookingService -> userService "Получает информацию о пользователе" "HTTPS/REST"
            bookingService -> paymentService "Инициирует платеж" "HTTPS/REST"
            bookingService -> messageQueue "Публикует события о бронировании" "AMQP"

            notificationService -> messageQueue "Подписан на события" "AMQP"

            paymentService -> paymentSystem "Обрабатывает платежи" "HTTPS/REST"
            notificationService -> emailSystem "Отправляет email" "SMTP"
            notificationService -> smsSystem "Отправляет SMS" "HTTPS/REST"
            hotelService -> mapsService "Получает геолокацию отелей" "HTTPS/REST"
        }

        bookingSystem -> paymentSystem "Обрабатывает платежи через" "HTTPS"
        bookingSystem -> emailSystem "Отправляет уведомления через" "SMTP"
        bookingSystem -> smsSystem "Отправляет SMS через" "HTTPS"
        bookingSystem -> mapsService "Получает данные о местоположении через" "HTTPS"
    }

    views {
        systemContext bookingSystem "SystemContext" {
            include *
            autoLayout
            description "Диаграмма контекста системы бронирования отелей"
        }

        container bookingSystem "Container" {
            include *
            autoLayout
            description "Диаграмма контейнеров системы бронирования отелей"
        }

        dynamic bookingSystem "CreateBooking" "Процесс создания бронирования отеля" {
            guest -> webApp "1. Выбирает отель и номер, заполняет данные бронирования"
            webApp -> apiGateway "2. POST /api/bookings"
            apiGateway -> bookingService "3. Создать бронирование"
            bookingService -> hotelService "4. Проверить доступность номера"
            hotelService -> hotelDB "5. Запросить данные о номере"
            hotelDB -> hotelService "6. Вернуть данные о номере"
            hotelService -> bookingService "7. Номер доступен"
            bookingService -> userService "8. Получить данные пользователя"
            userService -> userDB "9. Запросить данные пользователя"
            userDB -> userService "10. Вернуть данные пользователя"
            userService -> bookingService "11. Данные пользователя"
            bookingService -> paymentService "12. Инициировать платеж"
            paymentService -> paymentSystem "13. Обработать платеж"
            paymentSystem -> paymentService "14. Платеж успешен"
            paymentService -> bookingService "15. Платеж подтвержден"
            bookingService -> bookingDB "16. Сохранить бронирование"
            bookingService -> messageQueue "17. Опубликовать событие 'BookingCreated'"
            messageQueue -> notificationService "18. Получить событие"
            notificationService -> emailSystem "19. Отправить подтверждение на email"
            notificationService -> smsSystem "20. Отправить SMS уведомление"
            bookingService -> apiGateway "21. Вернуть подтверждение бронирования"
            apiGateway -> webApp "22. Показать подтверждение"
            webApp -> guest "23. Отобразить успешное бронирование"
            autoLayout
            description "Последовательность создания бронирования отеля"
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "WebBrowser" {
                shape WebBrowser
            }
            element "Mobile" {
                shape MobileDevicePortrait
            }
            element "Database" {
                shape Cylinder
                background #438dd5
            }
            element "Cache" {
                shape Cylinder
                background #ff6b6b
            }
            element "Queue" {
                shape Pipe
                background #f59e0b
            }
            element "Service" {
                shape Hexagon
            }
            element "API" {
                shape RoundedBox
                background #10b981
            }
        }

        theme default
    }

}
