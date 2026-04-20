import asyncio
from typing import Dict, Any

from .queue_data import broker, redis_client


class SystemHealthChecker:
    """Проверка здоровья компонентов системы"""

    def __init__(self, redis_client, broker):
        self.redis_client = redis_client
        self.broker = broker

    async def check_redis(self) -> Dict[str, Any]:
        """Проверка доступности Redis"""
        try:
            await asyncio.wait_for(self.redis_client.ping(), timeout=2.0)
            return {
                "available": True,
                "status": "healthy",
                "message": "Redis работает нормально",
            }
        except asyncio.TimeoutError:
            return {
                "available": False,
                "status": "timeout",
                "message": "Redis не отвечает (таймаут)",
            }
        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "message": f"Redis недоступен: {str(e)}",
            }

    async def check_worker(self) -> Dict[str, Any]:
        """Проверка наличия активных воркеров"""
        try:
            # Способ 1: Проверяем размер очереди и время последней обработки
            queue_key = "taskiq:default:queue"
            queue_size = await self.redis_client.llen(queue_key)

            # Способ 2: Если воркеры регистрируются в Redis
            workers_key = "taskiq:workers"
            workers = await self.redis_client.smembers(workers_key)
            active_workers = len(workers) if workers else 0

            # Способ 3: Проверяем, уменьшается ли очередь
            last_size_key = "last_queue_size"
            last_size = await self.redis_client.get(last_size_key)

            if active_workers > 0:
                return {
                    "available": True,
                    "status": "healthy",
                    "message": f"Активных воркеров: {active_workers}",
                    "workers_count": active_workers,
                    "queue_size": queue_size,
                }
            elif queue_size == 0:
                # Очередь пуста, но воркеров нет - возможно проблема
                return {
                    "available": False,
                    "status": "warning",
                    "message": "Нет активных воркеров, но очередь пуста",
                    "workers_count": 0,
                    "queue_size": 0,
                }
            else:
                # Очередь растет, воркеров нет - критично
                return {
                    "available": False,
                    "status": "critical",
                    "message": f"Нет воркеров! В очереди {queue_size} задач",
                    "workers_count": 0,
                    "queue_size": queue_size,
                }

        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "message": f"Не удалось проверить статус воркеров: {str(e)}",
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Полная проверка системы"""
        redis_status = await self.check_redis()
        worker_status = await self.check_worker()

        # Определяем общий статус
        if not redis_status["available"]:
            overall_status = "critical"
            message = "Система обработки недоступна (Redis не работает)"
        elif not worker_status["available"]:
            overall_status = "degraded"
            message = "Система работает с задержками (воркеры недоступны)"
        else:
            overall_status = "healthy"
            message = "Система работает нормально"

        return {
            "overall_status": overall_status,
            "message": message,
            "components": {"redis": redis_status, "worker": worker_status},
        }


# Создаем глобальный экземпляр
health_checker = SystemHealthChecker(redis_client, broker)
